import argparse
from pathlib import Path
from typing import Iterable

import ezdxf
from ezdxf.addons.importer import Importer


def _list_dxf_files(input_dir: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.dxf" if recursive else "*.dxf"
    files = sorted(p for p in input_dir.glob(pattern) if p.is_file())
    return files


def _collect_entities_by_layer(modelspace, target_layers_upper: set[str]) -> list:
    selected = []
    for entity in modelspace:
        layer_name = getattr(entity.dxf, "layer", "")
        if layer_name.upper() in target_layers_upper:
            selected.append(entity)
    return selected


def merge_dxf_files(
    input_dir: Path,
    output_file: Path,
    layers: Iterable[str],
    recursive: bool,
    keep_empty_output: bool,
) -> tuple[int, int]:
    dxf_files = _list_dxf_files(input_dir, recursive)
    if not dxf_files:
        raise FileNotFoundError(f"Nenhum arquivo DXF encontrado em: {input_dir}")

    target_layers_upper = {layer.strip().upper() for layer in layers if layer.strip()}
    if not target_layers_upper:
        raise ValueError("A lista de camadas nao pode estar vazia.")

    target_doc = ezdxf.new("R2010")
    target_msp = target_doc.modelspace()

    total_imported = 0
    files_with_data = 0

    for dxf_path in dxf_files:
        try:
            source_doc = ezdxf.readfile(dxf_path)
        except Exception as exc:
            print(f"[ERRO] Falha ao ler {dxf_path.name}: {exc}")
            continue

        source_msp = source_doc.modelspace()
        entities = _collect_entities_by_layer(source_msp, target_layers_upper)

        if not entities:
            print(f"[SKIP] {dxf_path.name}: sem entidades nas camadas alvo.")
            continue

        importer = Importer(source_doc, target_doc)
        importer.import_entities(entities, target_msp)
        importer.finalize()

        files_with_data += 1
        total_imported += len(entities)
        print(f"[OK] {dxf_path.name}: {len(entities)} entidades importadas.")

    if total_imported == 0 and not keep_empty_output:
        raise RuntimeError(
            "Nenhuma entidade foi importada. Verifique os nomes das camadas e os arquivos DXF."
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    target_doc.saveas(output_file)

    return files_with_data, total_imported


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compila varios DXF em um unico DXF, preservando coordenadas, "
            "filtrando por camadas (padrao: LIMITE_ROTA e SEQ_ROTA)."
        )
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Pasta com os arquivos DXF de entrada.",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Caminho do DXF de saida unico.",
    )
    parser.add_argument(
        "--layers",
        nargs="+",
        default=["LIMITE_ROTA", "SEQ_ROTA"],
        help="Lista de camadas a importar (separadas por espaco).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Busca arquivos DXF recursivamente em subpastas.",
    )
    parser.add_argument(
        "--keep-empty-output",
        action="store_true",
        help="Gera arquivo de saida mesmo se nenhuma entidade for importada.",
    )
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.input_dir.exists() or not args.input_dir.is_dir():
        raise NotADirectoryError(f"Pasta invalida: {args.input_dir}")

    files_with_data, total_imported = merge_dxf_files(
        input_dir=args.input_dir,
        output_file=args.output_file,
        layers=args.layers,
        recursive=args.recursive,
        keep_empty_output=args.keep_empty_output,
    )

    print("\nResumo:")
    print(f"- Arquivos com dados importados: {files_with_data}")
    print(f"- Total de entidades importadas: {total_imported}")
    print(f"- Arquivo de saida: {args.output_file}")


if __name__ == "__main__":
    main()

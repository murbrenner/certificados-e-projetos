def cpf_ok(cpf):
    ncpf = len(cpf)
    while ncpf < 11:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def documento(doc):
    ndoc = len(doc)
    if ndoc <= 11:
        tdoc = 1
        cpf = doc
    elif ndoc > 11:
        tdoc = 2
        cnpj = doc
    return doc

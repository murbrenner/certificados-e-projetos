def cpf_ok(cpf):
    ncpf = len(cpf)
    while ncpf < 11:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def cnpj_ok(cpf):
    ncpf = len(cpf)
    while ncpf < 14:
        cpf = "0" + cpf
        ncpf = ncpf + 1
    return cpf

def rg_ok(rg):
    nrg = len(rg)
    while nrg < 13:
        cpf = "0" + rg
        nrg = nrg + 1
    return rg
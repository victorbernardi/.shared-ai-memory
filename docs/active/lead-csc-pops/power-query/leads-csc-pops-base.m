// Power Query M — Importação de leads-csc-pops-base.xlsx via OneDrive (Web)
// Funciona em qualquer computador com acesso ao SharePoint da Inova.
// Autenticação: na primeira atualização, o Excel pedirá login com a conta Microsoft corporativa.
//
// Como configurar no Excel (leads-csc-pops-peças.xlsx):
//   1. Dados → Obter Dados → De Outras Fontes → Da Web
//   2. Cole a URL abaixo e confirme
//   3. Em seguida, substitua a query gerada automaticamente por este código via Editor Avançado
//   4. Ative "Atualizar dados ao abrir o arquivo" nas propriedades da conexão

let
    URL = "https://trevisomaq-my.sharepoint.com/personal/victor_bernardi_inovamaquinas_com/Documents/leads-csc-pops-base.xlsx",
    Fonte = Excel.Workbook(Web.Contents(URL), null, true),
    LeadsAtivos = Fonte{[Item="Leads Ativos", Kind="Sheet"]}[Data],
    CabecalhoPromovido = Table.PromoteHeaders(LeadsAtivos, [PromoteAllScalars=true]),
    ColunasRemovidas = Table.RemoveColumns(CabecalhoPromovido, {"Primeiro Alerta"}),
    TiposDefinidos = Table.TransformColumnTypes(ColunasRemovidas, {
        {"Chassi",             type text},
        {"Consultor",          type text},
        {"CSA",                type text},
        {"Nome do Cliente",    type text},
        {"CNPJ",               type text},
        {"Mesoregiao",         type text},
        {"Segmentacao",        type text},
        {"Modelo",             type text},
        {"Familia",            type text},
        {"Gatilho Alerta",     type text},
        {"Horimetro Atual",    type number},
        {"Horimetro Base",     type number},
        {"Delta Horimetro",    type number},
        {"Retorno do Contato", type text},
        {"Observacoes",        type text}
    })
in
    TiposDefinidos

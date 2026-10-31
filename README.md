# Desafio DevSecOps — Gerenciador de Tarefas

## Sobre o Projeto
Este repositório faz parte do desafio prático do módulo de DevSecOps da ADA Tech.
Você receberá este projeto com vulnerabilidades propositais e uma pipeline incompleta.
Seu objetivo é **implementar a pipeline de segurança** e **corrigir as vulnerabilidades**.

## Estado atual
A pipeline está **incompleta**. Os steps de segurança precisam ser implementados por você.

## Sua missão
1. Implementar os steps de segurança no `pipeline.yml`
2. Fazer a pipeline **quebrar** ao detectar os problemas
3. Corrigir as vulnerabilidades encontradas
4. Fazer a pipeline **passar** com tudo verde ✅
5. Documentar o funcionamento da pipeline neste README

## O que implementar
- [ ] Secrets Scanning com **Gitleaks**
- [x] SAST com **Semgrep**
- [ ] SCA com **Grype**
- [ ] Assinatura do artefato com cosign
- [ ] Deploy com **GitHub Pages**

## Como a pipeline funciona
> **Substitua este bloco pela sua explicação após implementar a pipeline.**
> Descreva cada step, o que ele faz e por que ele é importante para a segurança.

O step de SAST configura Python 3.12, instala o Semgrep e executa
`semgrep scan --config auto --config p/xss --error src/`.
As regras automáticas e de XSS analisam o código em `src/`; a opção `--error`
faz o step falhar quando encontra problemas, bloqueando o deploy.
Essa análise não exige token do Semgrep. As regras são baixadas do Registry.

## Observabilidade da pipeline com OpenTelemetry

Para criar o backend na Azure, siga o
[passo a passo do laboratório](AZURE-OBSERVABILIDADE.md), com VM, HTTPS,
Collector, Tempo, Grafana e procedimentos para ligar e desligar.
Para copiar os comandos na ordem de execução, use
[AZURE-COMANDOS.md](AZURE-COMANDOS.md), com indicação de Cloud Shell ou VM.

O workflow `.github/workflows/telemetry.yml` usa a action
[`dash0hq/otel-cicd-action`](https://github.com/marketplace/actions/open-telemetry-ci-cd-action),
fixada no commit da versão 4.2.0. Ela consulta a API do GitHub e transforma a
execução da pipeline, seus jobs e steps em spans de um trace. Isso permite
investigar duração, gargalos e falhas no backend de observabilidade. A action
exporta traces; não instrumenta o JavaScript da aplicação nem envia os arquivos
JSON produzidos pelo Semgrep e pelo Grype como relatórios.

A exportação roda em um workflow separado, disparado pelo evento
`workflow_run: completed` da `🔐 Pipeline DevSecOps`, inclusive quando ela falha
ou é cancelada. Assim, os jobs monitorados já terminaram quando os dados são
consultados. Uma falha de exportação fica visível no workflow de telemetria e
não altera o resultado da pipeline de build e deploy. O nome no filtro
`workflows` precisa acompanhar qualquer alteração no nome da pipeline.

### Configuração no GitHub

Em **Settings → Secrets and variables → Actions**, configure no nível do
repositório (o workflow de telemetria não usa o environment `github-pages`):

| Tipo | Nome | Valor |
| --- | --- | --- |
| Variable | `OTEL_EXPORTER_OTLP_ENDPOINT` | Endpoint OTLP acessível pelo runner, por exemplo `https://otel.example.com/v1/traces` para HTTP ou `grpc://otel.example.com:4317` para gRPC. Use o endereço indicado pelo seu provedor. |
| Secret | `OTEL_EXPORTER_OTLP_HEADERS` | Headers exigidos pelo backend, no formato `Authorization=Bearer TOKEN` ou múltiplos pares separados por vírgula. Para um collector sem autenticação, pode ficar ausente. |

É necessário fornecer um collector ou serviço compatível com OTLP; este projeto
não provisiona esse serviço. Sem a variável de endpoint, o job fica **skipped**.
O endpoint precisa ser alcançável pelo runner hospedado no GitHub; `localhost`
não aponta para sua máquina. A verificação TLS permanece habilitada.

O `GITHUB_TOKEN` é fornecido automaticamente com apenas `contents: read` e
`actions: read`. Não é necessário criar um token pessoal. O workflow não faz
checkout nem executa artefatos da execução monitorada. O uso de `workflow_run`
exige que o arquivo de telemetria esteja na branch padrão do repositório.

### Onde trocar o endereço do collector

No GitHub, abra **Settings → Secrets and variables → Actions → Variables**,
edite `OTEL_EXPORTER_OTLP_ENDPOINT` e salve a URL completa do novo endpoint.
Não é necessário alterar o YAML nem criar um commit. A próxima execução de
telemetria usará o novo endereço. Se o token mudar, atualize também
`OTEL_EXPORTER_OTLP_HEADERS` na aba **Secrets**.

Para HTTPS, prefira um nome DNS apontando para o IP atual e mantenha o
certificado válido para esse nome. Quando apenas o IP mudar, atualizar o DNS
permite conservar a mesma URL no GitHub. Não desabilite TLS para contornar
erros de certificado ao acessar diretamente pelo IP.

Na Azure, IPs públicos Basic foram aposentados em 30/09/2025; IPs públicos
Standard usam alocação estática. Para liberar a cobrança do IP entre sessões,
é necessário desassociar e excluir o recurso de IP público, recriando-o e
associando-o novamente no próximo uso. Isso é diferente de desalocar a VM,
que conserva o IP e sua cobrança. Ao recriar, atualize o DNS ou o endpoint
conforme sua configuração. Consulte a
[documentação de IPs públicos da Azure](https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/public-ip-addresses/).

### Como verificar

Após disponibilizar o workflow na branch padrão e configurar o backend, faça
um push na `main`. Quando a pipeline terminar, abra **Actions → 📊 Telemetria
da Pipeline** e confira o step de exportação. No backend, procure o serviço
`projeto-devsecop-desafio-ci` e verifique os spans dos jobs e steps, suas
durações e os estados de sucesso ou falha. Um bloqueio por uma análise de
segurança também deve aparecer no trace.

Os dados exportados incluem metadados do GitHub sem redação, como mensagem de
commit, nomes e e-mails de autores. Escolha um backend adequado para receber
esses dados. As permissões opcionais de leitura de PRs e checks não foram
concedidas. Consulte a seção de dados exportados da documentação da action
para avaliar os atributos enviados.

## URL de Produção
> Adicione aqui o link do GitHub Pages após o deploy.

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
- [x] Secrets Scanning com **Gitleaks**
- [x] SAST com **Semgrep**
- [x] SCA com **Grype**
- [x] Assinatura do artefato com cosign
- [x] Deploy com **GitHub Pages**

## Como a pipeline funciona
## Como a pipeline funciona
 
A pipeline é executada automaticamente a cada alteração enviada para a branch `main` e tem como objetivo garantir que apenas código seguro e validado seja publicado em produção. O fluxo foi organizado em duas etapas principais: construção e validação do artefato, seguida da verificação de integridade e publicação no GitHub Pages.
 
### 📥 Checkout do Código
 
O primeiro passo realiza o checkout completo do repositório utilizando `actions/checkout@v4`. Isso disponibiliza todo o histórico e os arquivos necessários para as análises de segurança e geração do artefato.
 
### 🔐 Inserção de Secrets
 
As credenciais armazenadas de forma segura nos Secrets do GitHub são injetadas durante a execução da pipeline. Dessa forma, informações sensíveis não ficam expostas no código-fonte nem versionadas no repositório.
 
### ⚙️ Build
 
O build valida a estrutura do projeto e garante que os arquivos necessários para execução da aplicação estejam disponíveis antes das análises de segurança.
 
### 🔑 Secrets Scanning com Gitleaks
 
O Gitleaks realiza a análise do repositório em busca de credenciais expostas, chaves de API, senhas e outros segredos que possam ter sido acidentalmente commitados.
 
Caso um segredo seja identificado, a pipeline é interrompida imediatamente, evitando que informações sensíveis sejam publicadas ou compartilhadas.
 
### 🔍 SAST (Static Application Security Testing) com Semgrep
 
O Semgrep executa uma análise estática do código-fonte em busca de falhas de segurança conhecidas, más práticas de desenvolvimento e vulnerabilidades comuns.
 
Foram utilizadas as regras automáticas do Semgrep (`--config auto`) juntamente com regras específicas para identificação de vulnerabilidades de Cross-Site Scripting (XSS) (`--config p/xss`).
 
A opção `--error` faz com que a pipeline seja interrompida quando vulnerabilidades são encontradas, impedindo que código inseguro avance para produção.
 
Além da análise, um relatório resumido é gerado para facilitar a identificação e correção dos problemas detectados.
 
### 📦 SCA (Software Composition Analysis) com Grype
 
O Grype analisa as dependências utilizadas pela aplicação em busca de vulnerabilidades conhecidas publicadas em bases como NVD e GitHub Security Advisories.
 
Primeiramente é gerado o arquivo `package-lock.json`, utilizado como referência das dependências instaladas. Em seguida, o Grype verifica versões vulneráveis de bibliotecas e componentes utilizados pelo projeto.
 
A configuração `--fail-on medium` faz com que a pipeline falhe ao encontrar vulnerabilidades classificadas com severidade Média, Alta ou Crítica.
 
Assim como o Semgrep, é gerado um relatório para auxiliar a correção dos problemas encontrados.
 
### 📦 Empacotamento do Artefato
 
Após a aprovação das verificações de segurança, os arquivos da aplicação são empacotados em um artefato único (`artifact.tar`), que será utilizado no processo de publicação.
 
### 🔢 Geração de Hash
 
É calculado um hash SHA-256 do artefato gerado. Esse hash funciona como uma impressão digital do pacote e permite verificar posteriormente se o conteúdo sofreu qualquer alteração.
 
### ✍️ Assinatura Digital com Cosign
 
O Cosign é utilizado para assinar digitalmente o artefato gerado.
 
A assinatura permite comprovar a autenticidade e a origem do pacote, garantindo que ele realmente foi produzido pela pipeline autorizada e não sofreu adulterações durante o processo.
 
O artefato assinado, seu hash e o bundle de assinatura são armazenados para as etapas seguintes.
 
### 🔎 Verificação de Assinatura
 
Antes da publicação, a assinatura digital é validada utilizando o Cosign.
 
Essa verificação garante a integridade do artefato e confirma que ele foi produzido pelo workflow autorizado do GitHub Actions. Caso a verificação falhe, o deploy é bloqueado automaticamente.
 
### 🌐 Publicação no GitHub Pages
 
Após todas as validações de segurança, o conteúdo é enviado para o GitHub Pages utilizando as actions oficiais do GitHub.
 
Somente artefatos que passaram pelas verificações de Secrets Scanning, SAST, SCA e validação de assinatura podem ser publicados.
 
### ✅ Benefícios de Segurança Implementados
 
- Detecção de segredos expostos com Gitleaks.
- Análise estática de código (SAST) com Semgrep.
- Análise de dependências vulneráveis (SCA) com Grype.
- Geração de hash para validação de integridade.
- Assinatura digital de artefatos com Cosign.
- Verificação de autenticidade antes do deploy.
- Bloqueio automático da publicação



## URL de Produção
> [URL DE PRODUÇÃO.](https://donaldserafim.github.io/projeto-devsecop-desafio/)

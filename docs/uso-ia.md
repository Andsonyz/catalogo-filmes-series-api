# Evidência de uso de inteligência artificial

A seção histórica a seguir foi recuperada de `docs/evidencias.md` no commit `a9f354b`. O prompt e a resposta foram mantidos literalmente, com os caminhos e o contexto da época.

## Evidência real de uso de IA — revisão do Prompt 4

**Ferramenta:** Codex, nesta conversa. As transcrições abaixo são a pergunta real do solicitante e a resposta efetivamente apresentada, sem reconstruir uma resposta hipotética. Caminhos e nomes de arquivos refletem o estado daquela revisão.

### Pergunta integral

```text
Revise os testes do cadastro de filmes e séries. Se um PATCH tentar mudar uma série de duas temporadas para filme enviando apenas o novo tipo, qual teste garante que a API rejeita a alteração e que tipo e temporadas continuam intactos no banco? Confira o código e identifique a asserção que detectaria uma alteração indevida. Se o cenário já estiver coberto, identifique um caso de borda relevante, verifique se já existe teste para ele e sugira uma melhoria pequena, ou justifique por que manter os testes atuais. Em até 120 palavras, indique o arquivo e o teste, a sugestão e como verificá-la. Responda apenas com o parecer nesta etapa. Deixe a árvore de trabalho intacta.
```

### Resposta integral apresentada pelo Codex

```markdown
Em [catalogo/tests.py](/workspace/catalogo-filmes-series-api/catalogo/tests.py), `test_patch_rejeita_conversao_para_filme_sem_limpar_temporadas` cobre a regra, embora envie também um nome novo. Exige HTTP 400 e, após `titulo.refresh_from_db()`, verifica `self.assertEqual(titulo.tipo, "serie")` e `self.assertEqual(titulo.numero_temporadas, 2)`. Essas asserções detectariam alteração indevida persistida.

Um caso de borda ainda sem teste é a conversão inversa: filme para série, omitindo temporadas. Sugiro adicionar um teste que espere 400 e confirme, após recarregar, tipo `filme` e temporadas nulas.

Verifique a melhoria com `venv/bin/python -m pytest catalogo/tests.py -v` e depois execute a suíte completa. Nenhum arquivo foi alterado nesta revisão.
```

### Sugestão gerada

Adicionar um teste para PATCH de filme para série omitindo `numero_temporadas`, conferindo rejeição e preservação do banco. A resposta também identificou a proteção já existente para a direção série → filme.

### Decisão técnica à luz do código

A sugestão trouxe benefício: `TituloSerializer.validate()` combina os valores recebidos com os já persistidos. Um filme possui temporadas nulas e, se receber somente `tipo: serie`, o estado final continuaria sem temporadas e deve ser rejeitado. Essa validação já existia na API, mas faltava um teste automatizado específico para a direção inversa. Portanto, a menor mudança adequada foi somente o teste `test_patch_rejeita_conversao_para_serie_sem_informar_temporadas`, aplicado no commit `575dd33`; não foi necessário mudar a regra de produção.

Para explicar em equipe: primeiro o teste cria um filme próprio; envia exatamente `{"tipo":"serie"}`; exige 400 e mensagem de temporadas; recarrega com `refresh_from_db()` e exige `tipo == "filme"` e `numero_temporadas is None`. Assim, não basta devolver erro: o banco também precisa permanecer intacto. Nome, gênero e contagem são conferidos. O teste válido de série → filme envia `null` explicitamente, demonstrando a diferença entre omitir um campo e limpá-lo.

### Resultado da validação e preservação do trabalho da equipe

A validação inicial da sugestão está no registro real [registro-teste-conversao.log](registro-teste-conversao.log): 1 teste específico, 15 do catálogo e 16 totais passaram. Ao iniciar esta etapa, `origin/main` estava em `87e43bb`, contendo o arquivo da equipe `catalogo/teste.py` e `docs/registro-teste.log`. Seu conteúdo correspondia aos 14 testes anteriores, mas `teste.py` não era reconhecido pelos padrões de descoberta existentes: após consolidar no nome da equipe e antes de ajustar o padrão, `venv/bin/python -m pytest --collect-only -q` encontrou apenas o teste herdado.

Preservado o nome `catalogo/teste.py`, incorporado nele o caso de borda e removida a cópia duplicada `catalogo/tests.py`. Acrescentado somente `teste.py` aos padrões de `pytest.ini`. Após a correção de descoberta, a suíte encontrou e aprovou 16 testes (15 da equipe e 1 herdado). O merge de atualização `ac3fa3d` preserva ambos os históricos; as evidências anteriores e o log acrescentado pela equipe foram mantidos. Esse problema de descoberta era de configuração do trabalho, não uma limitação do ambiente. Os nomes antigos nos registros históricos não foram reescritos como se os comandos tivessem sido executados com o nome novo.

O README agora usa o caminho atual `catalogo/teste.py`. A nova validação, métricas e confirmação da integração são registradas abaixo após sua execução. O relatório final não faz parte desta etapa.

## Conferência atual em 10/11/2026

O teste aceito está hoje em [catalogo/teste.py](../catalogo/teste.py), com o nome `test_patch_rejeita_conversao_para_serie_sem_informar_temporadas`. O serializer continua rejeitando a conversão de filme para série sem temporadas. O teste cria um filme, envia apenas o novo tipo, confere HTTP 400 e verifica, após `refresh_from_db()`, que tipo, temporadas, nome, gênero e quantidade foram preservados.

Na medição atual, a execução isolada desse teste resultou em **1 passed**, e a suíte completa executada sob coverage resultou em **33 passed**. Os comandos e resultados estão em [registro-metricas-atual.log](registro-metricas-atual.log). Nenhuma alteração à validação da API foi necessária para esta conferência.


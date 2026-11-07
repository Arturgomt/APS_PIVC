-- Cadastros da empresa química: instalações, produtos, fórmulas, processos e documentos.
-- Aplicar depois de "sistema biometria APS.sql". Pode ser executado mais de uma vez.
-- mysql -u root -p --default-character-set=utf8mb4 sistema_biometrico < migracao_empresa_quimica.sql
--
-- Hierarquia (usuarios.nivel_permissao): 1 Analista, 2 Diretor, 3 Ministro.
-- Cada item tem setor (divisoes), nível de sigilo e status (rascunho/aprovado).
-- As regras de quem vê, edita e aprova ficam em api.py (pode_ver, pode_editar, pode_aprovar).

SET NAMES utf8mb4;
USE sistema_biometrico;

CREATE TABLE IF NOT EXISTS instalacoes (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  tipo ENUM('Fábrica','Laboratório','Depósito','Escritório') NOT NULL,
  cidade VARCHAR(100) DEFAULT NULL,
  licenca_ambiental VARCHAR(60) DEFAULT NULL,
  licenca_validade DATE DEFAULT NULL,
  setor_id INT DEFAULT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_instalacoes_nome (nome),
  CONSTRAINT fk_instalacoes_setor FOREIGN KEY (setor_id) REFERENCES divisoes (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS produtos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(30) NOT NULL,
  nome VARCHAR(150) NOT NULL,
  cas VARCHAR(20) DEFAULT NULL,
  classe_risco VARCHAR(80) DEFAULT NULL,
  estado_fisico ENUM('Sólido','Líquido','Gasoso') NOT NULL DEFAULT 'Líquido',
  unidade ENUM('kg','L','t','m³') NOT NULL DEFAULT 'kg',
  estoque DECIMAL(14,3) NOT NULL DEFAULT 0,
  instalacao_id INT DEFAULT NULL,
  descricao TEXT,
  setor_id INT NOT NULL,
  nivel_sigilo TINYINT NOT NULL DEFAULT 1,
  status ENUM('rascunho','aprovado') NOT NULL DEFAULT 'rascunho',
  criado_por INT DEFAULT NULL,
  aprovado_por INT DEFAULT NULL,
  aprovado_em DATETIME DEFAULT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_produtos_codigo (codigo),
  CONSTRAINT fk_produtos_instalacao FOREIGN KEY (instalacao_id) REFERENCES instalacoes (id),
  CONSTRAINT fk_produtos_setor FOREIGN KEY (setor_id) REFERENCES divisoes (id),
  CONSTRAINT fk_produtos_autor FOREIGN KEY (criado_por) REFERENCES usuarios (id),
  CONSTRAINT fk_produtos_aprovador FOREIGN KEY (aprovado_por) REFERENCES usuarios (id),
  CONSTRAINT chk_produtos_nivel CHECK (nivel_sigilo BETWEEN 1 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS formulas (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  produto_id INT NOT NULL,
  versao VARCHAR(20) NOT NULL,
  componentes JSON NOT NULL,
  observacoes TEXT,
  setor_id INT NOT NULL,
  nivel_sigilo TINYINT NOT NULL DEFAULT 3,
  status ENUM('rascunho','aprovado') NOT NULL DEFAULT 'rascunho',
  criado_por INT DEFAULT NULL,
  aprovado_por INT DEFAULT NULL,
  aprovado_em DATETIME DEFAULT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_formulas_versao (produto_id, versao),
  CONSTRAINT fk_formulas_produto FOREIGN KEY (produto_id) REFERENCES produtos (id),
  CONSTRAINT fk_formulas_setor FOREIGN KEY (setor_id) REFERENCES divisoes (id),
  CONSTRAINT fk_formulas_autor FOREIGN KEY (criado_por) REFERENCES usuarios (id),
  CONSTRAINT fk_formulas_aprovador FOREIGN KEY (aprovado_por) REFERENCES usuarios (id),
  CONSTRAINT chk_formulas_nivel CHECK (nivel_sigilo BETWEEN 1 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS processos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(150) NOT NULL,
  produto_id INT NOT NULL,
  instalacao_id INT DEFAULT NULL,
  etapas TEXT NOT NULL,
  parametros TEXT,
  epis TEXT,
  setor_id INT NOT NULL,
  nivel_sigilo TINYINT NOT NULL DEFAULT 2,
  status ENUM('rascunho','aprovado') NOT NULL DEFAULT 'rascunho',
  criado_por INT DEFAULT NULL,
  aprovado_por INT DEFAULT NULL,
  aprovado_em DATETIME DEFAULT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_processos_nome (nome),
  CONSTRAINT fk_processos_produto FOREIGN KEY (produto_id) REFERENCES produtos (id),
  CONSTRAINT fk_processos_instalacao FOREIGN KEY (instalacao_id) REFERENCES instalacoes (id),
  CONSTRAINT fk_processos_setor FOREIGN KEY (setor_id) REFERENCES divisoes (id),
  CONSTRAINT fk_processos_autor FOREIGN KEY (criado_por) REFERENCES usuarios (id),
  CONSTRAINT fk_processos_aprovador FOREIGN KEY (aprovado_por) REFERENCES usuarios (id),
  CONSTRAINT chk_processos_nivel CHECK (nivel_sigilo BETWEEN 1 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS documentos (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(200) NOT NULL,
  tipo ENUM('FISPQ','Bula','POP','Laudo','Licença','Patente','Outro') NOT NULL,
  produto_id INT DEFAULT NULL,
  versao VARCHAR(20) NOT NULL DEFAULT '1.0',
  validade DATE DEFAULT NULL,
  conteudo TEXT NOT NULL,
  setor_id INT NOT NULL,
  nivel_sigilo TINYINT NOT NULL DEFAULT 1,
  status ENUM('rascunho','aprovado') NOT NULL DEFAULT 'rascunho',
  criado_por INT DEFAULT NULL,
  aprovado_por INT DEFAULT NULL,
  aprovado_em DATETIME DEFAULT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  atualizado_em DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_documentos_titulo (titulo, versao),
  CONSTRAINT fk_documentos_produto FOREIGN KEY (produto_id) REFERENCES produtos (id),
  CONSTRAINT fk_documentos_setor FOREIGN KEY (setor_id) REFERENCES divisoes (id),
  CONSTRAINT fk_documentos_autor FOREIGN KEY (criado_por) REFERENCES usuarios (id),
  CONSTRAINT fk_documentos_aprovador FOREIGN KEY (aprovado_por) REFERENCES usuarios (id),
  CONSTRAINT chk_documentos_nivel CHECK (nivel_sigilo BETWEEN 1 AND 3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

UPDATE niveis_acesso SET nome = 'Analista', descricao = 'Nível 1: informações internas da empresa' WHERE codigo = 1;
UPDATE niveis_acesso SET nome = 'Diretor', descricao = 'Nível 2: informações restritas ao setor do diretor' WHERE codigo = 2;
UPDATE niveis_acesso SET nome = 'Ministro', descricao = 'Nível 3: informações confidenciais, como fórmulas e patentes' WHERE codigo = 3;

-- ---------- Dados fictícios de exemplo ----------

INSERT IGNORE INTO divisoes (nome, descricao) VALUES
  ('Produção', 'Operação das plantas e reatores'),
  ('Qualidade', 'Laboratório de controle e laudos'),
  ('P&D', 'Pesquisa e desenvolvimento de formulações'),
  ('SSMA', 'Saúde, segurança e meio ambiente'),
  ('Logística', 'Armazenagem e expedição'),
  ('Diretoria', 'Diretoria executiva');

INSERT IGNORE INTO instalacoes (nome, tipo, cidade, licenca_ambiental, licenca_validade, setor_id)
SELECT 'Unidade Fabril Cubatão', 'Fábrica', 'Cubatão/SP', 'LO 31.204/2024', '2028-03-31', id FROM divisoes WHERE nome = 'Produção'
UNION ALL SELECT 'Laboratório Central de Qualidade', 'Laboratório', 'Santo André/SP', NULL, NULL, id FROM divisoes WHERE nome = 'Qualidade'
UNION ALL SELECT 'Depósito de Inflamáveis e Corrosivos', 'Depósito', 'Cubatão/SP', 'LO 31.877/2022', '2026-12-15', id FROM divisoes WHERE nome = 'Logística'
UNION ALL SELECT 'Centro de P&D', 'Laboratório', 'Campinas/SP', NULL, NULL, id FROM divisoes WHERE nome = 'P&D';

INSERT IGNORE INTO produtos (codigo, nome, cas, classe_risco, estado_fisico, unidade, estoque, instalacao_id, descricao, setor_id, nivel_sigilo, status, aprovado_em)
SELECT p.codigo, p.nome, p.cas, p.risco, 'Líquido', p.unidade, p.estoque, i.id, p.descricao, d.id, 1, p.status, IF(p.status = 'aprovado', NOW(), NULL)
FROM (
  SELECT 'PQ-001' codigo, 'Ácido Sulfúrico 98%' nome, '7664-93-9' cas, 'ONU 1830 · Classe 8 (corrosivo)' risco, 't' unidade, 42.5 estoque,
         'Depósito de Inflamáveis e Corrosivos' inst, 'Produção' setor, 'aprovado' status, 'Matéria-prima para sulfonação e ajuste de pH.' descricao
  UNION ALL SELECT 'PQ-002', 'Hidróxido de Sódio 50%', '1310-73-2', 'ONU 1824 · Classe 8 (corrosivo)', 't', 18, 'Depósito de Inflamáveis e Corrosivos', 'Produção', 'aprovado', 'Soda cáustica líquida para neutralização.'
  UNION ALL SELECT 'PQ-003', 'Hipoclorito de Sódio 12%', '7681-52-9', 'ONU 1791 · Classe 8 (corrosivo)', 'L', 15000, 'Unidade Fabril Cubatão', 'Produção', 'aprovado', 'Agente oxidante e sanitizante.'
  UNION ALL SELECT 'PQ-004', 'Etanol 96%', '64-17-5', 'ONU 1170 · Classe 3 (inflamável)', 'L', 8000, 'Depósito de Inflamáveis e Corrosivos', 'Logística', 'aprovado', 'Solvente.'
  UNION ALL SELECT 'PQ-010', 'Desengraxante Industrial DX-200', NULL, 'Não classificado para transporte', 'L', 2500, 'Unidade Fabril Cubatão', 'P&D', 'aprovado', 'Produto de formulação própria para limpeza pesada.'
  UNION ALL SELECT 'PQ-011', 'Sanitizante Clorado SC-50', NULL, 'ONU 1791 · Classe 8 (corrosivo)', 'L', 0, 'Unidade Fabril Cubatão', 'Qualidade', 'rascunho', 'Lançamento previsto; aguardando aprovação.'
) p JOIN divisoes d ON d.nome = p.setor JOIN instalacoes i ON i.nome = p.inst;

INSERT IGNORE INTO formulas (produto_id, versao, componentes, observacoes, setor_id, nivel_sigilo, status, aprovado_em)
SELECT pr.id, '2.1', JSON_ARRAY(
    JSON_OBJECT('nome', 'Água deionizada', 'cas', '7732-18-5', 'percentual', 62),
    JSON_OBJECT('nome', 'Butilglicol', 'cas', '111-76-2', 'percentual', 15),
    JSON_OBJECT('nome', 'Álcool graxo etoxilado', 'cas', '68439-46-3', 'percentual', 10),
    JSON_OBJECT('nome', 'Metassilicato de sódio', 'cas', '6834-92-0', 'percentual', 8),
    JSON_OBJECT('nome', 'EDTA tetrassódico', 'cas', '64-02-8', 'percentual', 3),
    JSON_OBJECT('nome', 'Fragrância cítrica', 'cas', '', 'percentual', 2)),
  'Adicionar o metassilicato somente após dissolução completa do tensoativo.', d.id, 3, 'aprovado', NOW()
FROM produtos pr JOIN divisoes d ON d.nome = 'P&D' WHERE pr.codigo = 'PQ-010'
UNION ALL
SELECT pr.id, '1.0', JSON_ARRAY(
    JSON_OBJECT('nome', 'Água deionizada', 'cas', '7732-18-5', 'percentual', 55.5),
    JSON_OBJECT('nome', 'Hipoclorito de sódio 12%', 'cas', '7681-52-9', 'percentual', 42),
    JSON_OBJECT('nome', 'Hidróxido de sódio 50%', 'cas', '1310-73-2', 'percentual', 2),
    JSON_OBJECT('nome', 'Tensoativo anfótero', 'cas', '', 'percentual', 0.5)),
  'Versão em teste no laboratório.', d.id, 3, 'rascunho', NULL
FROM produtos pr JOIN divisoes d ON d.nome = 'P&D' WHERE pr.codigo = 'PQ-011';

INSERT IGNORE INTO processos (nome, produto_id, instalacao_id, etapas, parametros, epis, setor_id, nivel_sigilo, status, aprovado_em)
SELECT 'Fabricação do DX-200 (lote de 5.000 L)', pr.id, i.id,
  '1. Carregar o reator R-02 com água deionizada.\n2. Aquecer a 45 °C sob agitação.\n3. Adicionar butilglicol e tensoativo.\n4. Adicionar metassilicato e EDTA.\n5. Resfriar, adicionar fragrância e coletar amostra para o laboratório.',
  'Temperatura 40–50 °C · Agitação 120 rpm · pH final 12,0–12,5', 'Luvas nitrílicas, óculos de ampla visão, avental de PVC',
  d.id, 2, 'aprovado', NOW()
FROM produtos pr JOIN instalacoes i ON i.nome = 'Unidade Fabril Cubatão' JOIN divisoes d ON d.nome = 'Produção' WHERE pr.codigo = 'PQ-010'
UNION ALL
SELECT 'Diluição de Ácido Sulfúrico 98% para 70%', pr.id, i.id,
  '1. Encher o tanque de diluição com água fria.\n2. Adicionar o ácido lentamente sobre a água, nunca o contrário.\n3. Manter o resfriamento ligado até estabilizar.',
  'Temperatura máxima 60 °C · Vazão de ácido 200 L/h', 'Máscara facial, luvas de neoprene, roupa antiácida, botas de PVC',
  d.id, 2, 'aprovado', NOW()
FROM produtos pr JOIN instalacoes i ON i.nome = 'Unidade Fabril Cubatão' JOIN divisoes d ON d.nome = 'Produção' WHERE pr.codigo = 'PQ-001';

INSERT IGNORE INTO documentos (titulo, tipo, produto_id, versao, validade, conteudo, setor_id, nivel_sigilo, status, aprovado_em)
SELECT doc.titulo, doc.tipo, pr.id, doc.versao, doc.validade, doc.conteudo, d.id, doc.nivel, doc.status, IF(doc.status = 'aprovado', NOW(), NULL)
FROM (
  SELECT 'FISPQ — Ácido Sulfúrico 98%' titulo, 'FISPQ' tipo, 'PQ-001' produto, '3.0' versao, CAST(NULL AS DATE) validade, 1 nivel, 'Qualidade' setor, 'aprovado' status,
         'Perigos: provoca queimaduras graves na pele e lesões oculares.\nPrimeiros socorros: lavar com água em abundância por 15 minutos e procurar atendimento médico.\nArmazenamento: local ventilado, longe de bases e materiais orgânicos.' conteudo
  UNION ALL SELECT 'Bula técnica — Desengraxante DX-200', 'Bula', 'PQ-010', '2.1', NULL, 1, 'P&D', 'aprovado',
         'Uso: diluir de 1:10 a 1:40 em água conforme a sujidade.\nAplicação: pulverizar, aguardar 5 minutos e enxaguar.\nNão misturar com produtos ácidos.'
  UNION ALL SELECT 'POP-PRD-007 — Carregamento de reatores', 'POP', NULL, '1.4', '2027-06-30', 2, 'Produção', 'aprovado',
         'Objetivo: padronizar o carregamento dos reatores R-01 a R-04.\nResponsável: operador de produção sob supervisão do líder de turno.\nConferir a ordem de produção, o EPI e o aterramento antes de iniciar.'
  UNION ALL SELECT 'Laudo de análise — DX-200 lote 2611-04', 'Laudo', 'PQ-010', '1.0', NULL, 2, 'Qualidade', 'aprovado',
         'pH: 12,3 (especificação 12,0–12,5) · Densidade: 1,04 g/mL · Aparência: líquido límpido. Resultado: APROVADO.'
  UNION ALL SELECT 'Pedido de patente — estabilização do DX-200', 'Patente', 'PQ-010', '1.0', NULL, 3, 'P&D', 'aprovado',
         'Reivindicação principal: uso combinado de metassilicato e EDTA para estabilizar o tensoativo em pH acima de 12.'
  UNION ALL SELECT 'Licença de Operação — Depósito de Cubatão', 'Licença', NULL, '2022', '2026-12-15', 2, 'Logística', 'aprovado',
         'Licença de operação para armazenamento de inflamáveis e corrosivos. Renovação deve ser solicitada 120 dias antes do vencimento.'
) doc JOIN divisoes d ON d.nome = doc.setor LEFT JOIN produtos pr ON pr.codigo = doc.produto;

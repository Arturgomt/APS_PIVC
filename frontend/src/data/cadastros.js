import { Atom, Building2, Factory, FileText, FlaskConical, Workflow } from 'lucide-react';
import { dateOnly, daysUntil } from '../utils/format';

export const PERFIS = { 1: 'Analista', 2: 'Diretor', 3: 'Ministro' };
export const NIVEIS = { 1: 'Interno', 2: 'Restrito ao setor', 3: 'Confidencial' };

const validade = (value) => value ? `${dateOnly(value)}${daysUntil(value) <= 120 ? ' (vencendo)' : ''}` : '—';

// Telas geradas por CadastroPage. Campos: tipo text (padrão) | textarea | number | date | select | ref | componentes | nivel.
// nivelMinimo só decide o menu; quem vê, edita e aprova é decidido pela API.
export const CADASTROS = [
  {
    rota: 'produtos', titulo: 'Produtos', singular: 'produto', icone: FlaskConical, nivelMinimo: 1,
    colunas: [['codigo', 'Código'], ['nome', 'Produto'], ['cas', 'Nº CAS'], ['classe_risco', 'Risco'], ['instalacao', 'Instalação'],
      ['estoque', 'Estoque', (v, i) => `${Number(v).toLocaleString('pt-BR')} ${i.unidade}`]],
    campos: [
      { k: 'codigo', l: 'Código', req: true, ph: 'PQ-001' },
      { k: 'nome', l: 'Nome', req: true },
      { k: 'cas', l: 'Nº CAS', ph: '7664-93-9' },
      { k: 'classe_risco', l: 'Classe de risco (ONU/GHS)', ph: 'ONU 1830 · Classe 8 (corrosivo)' },
      { k: 'estado_fisico', l: 'Estado físico', tipo: 'select', opcoes: ['Líquido', 'Sólido', 'Gasoso'] },
      { k: 'unidade', l: 'Unidade', tipo: 'select', opcoes: ['kg', 'L', 't', 'm³'] },
      { k: 'estoque', l: 'Estoque', tipo: 'number' },
      { k: 'instalacao_id', l: 'Instalação', tipo: 'ref', ref: 'instalacoes', nome: 'instalacao' },
      { k: 'descricao', l: 'Descrição', tipo: 'textarea', largo: true },
    ],
  },
  {
    rota: 'processos', titulo: 'Processos', singular: 'processo', icone: Workflow, nivelMinimo: 2,
    colunas: [['nome', 'Processo'], ['produto', 'Produto'], ['instalacao', 'Instalação']],
    campos: [
      { k: 'nome', l: 'Nome do processo', req: true, largo: true },
      { k: 'produto_id', l: 'Produto', tipo: 'ref', ref: 'produtos', nome: 'produto', req: true },
      { k: 'instalacao_id', l: 'Instalação', tipo: 'ref', ref: 'instalacoes', nome: 'instalacao' },
      { k: 'etapas', l: 'Etapas', tipo: 'textarea', largo: true, req: true },
      { k: 'parametros', l: 'Parâmetros de controle', tipo: 'textarea', largo: true },
      { k: 'epis', l: 'EPIs obrigatórios', tipo: 'textarea', largo: true },
    ],
  },
  {
    rota: 'formulas', titulo: 'Fórmulas', singular: 'fórmula', feminino: true, icone: Atom, nivelMinimo: 3,
    colunas: [['produto', 'Produto'], ['versao', 'Versão']],
    campos: [
      { k: 'produto_id', l: 'Produto', tipo: 'ref', ref: 'produtos', nome: 'produto', req: true },
      { k: 'versao', l: 'Versão', req: true, ph: '1.0' },
      { k: 'componentes', l: 'Componentes', tipo: 'componentes', largo: true, req: true },
      { k: 'observacoes', l: 'Observações', tipo: 'textarea', largo: true },
    ],
  },
  {
    rota: 'documentos', titulo: 'Documentos', singular: 'documento', icone: FileText, nivelMinimo: 1,
    colunas: [['titulo', 'Documento'], ['tipo', 'Tipo'], ['produto', 'Produto'], ['versao', 'Versão'], ['validade', 'Validade', validade]],
    campos: [
      { k: 'titulo', l: 'Título', req: true, largo: true },
      { k: 'tipo', l: 'Tipo', tipo: 'select', opcoes: ['FISPQ', 'Bula', 'POP', 'Laudo', 'Licença', 'Patente', 'Outro'] },
      { k: 'nivel_sigilo', l: 'Nível de sigilo', tipo: 'nivel' },
      { k: 'produto_id', l: 'Produto', tipo: 'ref', ref: 'produtos', nome: 'produto' },
      { k: 'versao', l: 'Versão', req: true, ph: '1.0' },
      { k: 'validade', l: 'Validade', tipo: 'date' },
      { k: 'conteudo', l: 'Conteúdo', tipo: 'textarea', largo: true, req: true },
    ],
  },
  {
    rota: 'instalacoes', titulo: 'Instalações', singular: 'instalação', feminino: true, icone: Factory, nivelMinimo: 1, estrutural: true,
    colunas: [['nome', 'Instalação'], ['tipo', 'Tipo'], ['cidade', 'Cidade'], ['setor', 'Setor responsável'],
      ['licenca_validade', 'Licença válida até', validade]],
    campos: [
      { k: 'nome', l: 'Nome', req: true, largo: true },
      { k: 'tipo', l: 'Tipo', tipo: 'select', opcoes: ['Fábrica', 'Laboratório', 'Depósito', 'Escritório'] },
      { k: 'cidade', l: 'Cidade', ph: 'Cubatão/SP' },
      { k: 'licenca_ambiental', l: 'Licença ambiental', ph: 'LO 31.204/2024' },
      { k: 'licenca_validade', l: 'Validade da licença', tipo: 'date' },
      { k: 'setor_id', l: 'Setor responsável', tipo: 'ref', ref: 'setores', nome: 'setor' },
    ],
  },
  {
    rota: 'setores', titulo: 'Setores', singular: 'setor', icone: Building2, nivelMinimo: 1, estrutural: true, apenasAdmin: true,
    colunas: [['nome', 'Setor'], ['descricao', 'Descrição']],
    campos: [{ k: 'nome', l: 'Nome', req: true, largo: true }, { k: 'descricao', l: 'Descrição', tipo: 'textarea', largo: true }],
  },
];

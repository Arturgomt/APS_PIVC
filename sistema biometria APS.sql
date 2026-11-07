CREATE DATABASE  IF NOT EXISTS `sistema_biometrico` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `sistema_biometrico`;
-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: sistema_biometrico
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `amostras_faciais`
--

DROP TABLE IF EXISTS `amostras_faciais`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `amostras_faciais` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cadastro_facial_id` int NOT NULL,
  `ordem` int NOT NULL,
  `embedding` json NOT NULL,
  `brilho_medio` float DEFAULT NULL,
  `variancia_laplaciano` float DEFAULT NULL,
  `confianca_deteccao` float DEFAULT NULL,
  `capturado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_aps_amostra_ordem` (`cadastro_facial_id`,`ordem`),
  CONSTRAINT `fk_aps_amostra_cadastro` FOREIGN KEY (`cadastro_facial_id`) REFERENCES `cadastros_faciais` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `amostras_faciais`
--

LOCK TABLES `amostras_faciais` WRITE;
/*!40000 ALTER TABLE `amostras_faciais` DISABLE KEYS */;
/*!40000 ALTER TABLE `amostras_faciais` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `biometria`
--

DROP TABLE IF EXISTS `biometria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `biometria` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `caminho_imagem` varchar(255) DEFAULT NULL,
  `vetor_biometrico` text NOT NULL,
  `data_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `biometria_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `biometria`
--

LOCK TABLES `biometria` WRITE;
/*!40000 ALTER TABLE `biometria` DISABLE KEYS */;
INSERT INTO `biometria` VALUES (1,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 16:52:46'),(2,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 16:53:12'),(3,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 16:54:45'),(5,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:10:39'),(7,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:12:15'),(9,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:13:10'),(11,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:13:14'),(13,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:13:46'),(15,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:14:07'),(17,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:14:22'),(19,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:16:29'),(21,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:16:46'),(23,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:26:30'),(25,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:38:21'),(27,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 17:39:07'),(29,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 18:59:46'),(31,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-24 19:00:35'),(33,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-27 11:20:36'),(35,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-27 11:20:53'),(37,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-27 11:20:59'),(39,7,'testes/rosto_teste.jpg','VETOR_FICTICIO_TESTE','2026-10-27 11:22:12');
/*!40000 ALTER TABLE `biometria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cadastros_faciais`
--

DROP TABLE IF EXISTS `cadastros_faciais`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cadastros_faciais` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `configuracao_id` int NOT NULL,
  `status` varchar(20) NOT NULL DEFAULT 'ativo',
  `cadastrado_por` int DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `desativado_em` datetime DEFAULT NULL,
  `usuario_ativo_id` int GENERATED ALWAYS AS ((case when (`status` = _utf8mb4'ativo') then `usuario_id` else NULL end)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_aps_cadastro_ativo` (`usuario_ativo_id`),
  KEY `ix_aps_cadastro_usuario` (`usuario_id`),
  KEY `fk_aps_cf_config` (`configuracao_id`),
  KEY `fk_aps_cf_conta` (`cadastrado_por`),
  CONSTRAINT `fk_aps_cf_config` FOREIGN KEY (`configuracao_id`) REFERENCES `configuracoes_biometricas` (`id`),
  CONSTRAINT `fk_aps_cf_conta` FOREIGN KEY (`cadastrado_por`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_aps_cf_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `chk_aps_cf_status` CHECK ((`status` in (_utf8mb4'ativo',_utf8mb4'substituido',_utf8mb4'revogado')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cadastros_faciais`
--

LOCK TABLES `cadastros_faciais` WRITE;
/*!40000 ALTER TABLE `cadastros_faciais` DISABLE KEYS */;
/*!40000 ALTER TABLE `cadastros_faciais` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuracoes_biometricas`
--

DROP TABLE IF EXISTS `configuracoes_biometricas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuracoes_biometricas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `modelo_nome` varchar(100) NOT NULL,
  `modelo_versao` varchar(100) NOT NULL,
  `modelo_sha256` char(64) DEFAULT NULL,
  `dimensao_embedding` int NOT NULL,
  `contrato_preprocessamento` varchar(150) NOT NULL,
  `parametros_preprocessamento` json DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_aps_config_modelo` (`modelo_nome`,`modelo_versao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuracoes_biometricas`
--

LOCK TABLES `configuracoes_biometricas` WRITE;
/*!40000 ALTER TABLE `configuracoes_biometricas` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuracoes_biometricas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `contas`
--

DROP TABLE IF EXISTS `contas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `contas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `login` varchar(254) NOT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `papel` varchar(20) NOT NULL DEFAULT 'usuario',
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `ultimo_login_em` datetime DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `atualizado_em` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_contas_usuario` (`usuario_id`),
  UNIQUE KEY `uq_contas_login` (`login`),
  CONSTRAINT `fk_contas_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `chk_contas_papel` CHECK ((`papel` in (_utf8mb4'administrador',_utf8mb4'usuario')))
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `contas`
--

LOCK TABLES `contas` WRITE;
/*!40000 ALTER TABLE `contas` DISABLE KEYS */;
INSERT INTO `contas` VALUES (6,6,'joao','hash_da_senha','usuario',1,NULL,'2026-10-24 12:22:37',NULL),(7,7,'teste_nivel1','HASH_DE_TESTE_NAO_USAR','usuario',1,NULL,'2026-10-24 12:22:38',NULL),(27,27,'diretor_teste','HASH_FICTICIO','usuario',1,NULL,'2026-10-24 12:48:51',NULL),(28,28,'ministro_teste','HASH_FICTICIO','usuario',1,NULL,'2026-10-24 12:48:51',NULL);
/*!40000 ALTER TABLE `contas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `divisoes`
--

DROP TABLE IF EXISTS `divisoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `divisoes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` text,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `atualizado_em` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_divisoes_nome` (`nome`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `divisoes`
--

LOCK TABLES `divisoes` WRITE;
/*!40000 ALTER TABLE `divisoes` DISABLE KEYS */;
/*!40000 ALTER TABLE `divisoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eventos_administrativos`
--

DROP TABLE IF EXISTS `eventos_administrativos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eventos_administrativos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `conta_responsavel_id` int NOT NULL,
  `acao` varchar(50) NOT NULL,
  `entidade` varchar(50) NOT NULL,
  `registro_id` varchar(50) DEFAULT NULL,
  `detalhes` json DEFAULT NULL,
  `ocorrido_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_aps_eventos_responsavel` (`conta_responsavel_id`,`ocorrido_em`),
  KEY `ix_aps_eventos_entidade` (`entidade`,`registro_id`),
  CONSTRAINT `fk_aps_eventos_conta` FOREIGN KEY (`conta_responsavel_id`) REFERENCES `contas` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eventos_administrativos`
--

LOCK TABLES `eventos_administrativos` WRITE;
/*!40000 ALTER TABLE `eventos_administrativos` DISABLE KEYS */;
/*!40000 ALTER TABLE `eventos_administrativos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `informacoes_protegidas`
--

DROP TABLE IF EXISTS `informacoes_protegidas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `informacoes_protegidas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(150) NOT NULL,
  `descricao` text,
  `conteudo` text NOT NULL,
  `nivel_minimo_id` int NOT NULL,
  `data_cadastro` datetime DEFAULT CURRENT_TIMESTAMP,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `fk_info_protegidas_nivel` (`nivel_minimo_id`),
  CONSTRAINT `fk_info_protegidas_nivel` FOREIGN KEY (`nivel_minimo_id`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `informacoes_protegidas`
--

LOCK TABLES `informacoes_protegidas` WRITE;
/*!40000 ALTER TABLE `informacoes_protegidas` DISABLE KEYS */;
INSERT INTO `informacoes_protegidas` VALUES (1,'Informacao Geral','Informacao basica do sistema','Conteudo de teste para o nivel geral',1,'2026-10-28 15:42:11',1),(2,'Relatorio da Diretoria','Informacao destinada aos diretores','Conteudo ficticio restrito a diretoria',2,'2026-10-28 15:42:11',1),(3,'Relatorio Ministerial','Informacao restrita ao ministro','Conteudo ficticio confidencial',3,'2026-10-28 15:42:11',1);
/*!40000 ALTER TABLE `informacoes_protegidas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `niveis_acesso`
--

DROP TABLE IF EXISTS `niveis_acesso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `niveis_acesso` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` int NOT NULL,
  `nome` varchar(50) NOT NULL,
  `descricao` text,
  `exige_divisao` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_niveis_codigo` (`codigo`),
  UNIQUE KEY `uq_niveis_nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `niveis_acesso`
--

LOCK TABLES `niveis_acesso` WRITE;
/*!40000 ALTER TABLE `niveis_acesso` DISABLE KEYS */;
INSERT INTO `niveis_acesso` VALUES (1,1,'Geral','Acesso geral autorizado',0),(2,2,'Diretoria','Acesso restrito a divisões específicas',1),(3,3,'Ministro','Acesso exclusivo ao ministro do Meio Ambiente',0);
/*!40000 ALTER TABLE `niveis_acesso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes`
--

DROP TABLE IF EXISTS `permissoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes` (
  `id` int NOT NULL,
  `nome` varchar(50) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes`
--

LOCK TABLES `permissoes` WRITE;
/*!40000 ALTER TABLE `permissoes` DISABLE KEYS */;
INSERT INTO `permissoes` VALUES (1,'Geral','Acesso geral autorizado'),(2,'Diretor','Acesso restrito a divisões específicas'),(3,'Ministro','Acesso exclusivo ao ministro do Meio Ambiente');
/*!40000 ALTER TABLE `permissoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissoes_usuarios`
--

DROP TABLE IF EXISTS `permissoes_usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissoes_usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `nivel_id` int NOT NULL,
  `divisao_id` int DEFAULT NULL,
  `concedido_por` int DEFAULT NULL,
  `concedido_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `expira_em` datetime DEFAULT NULL,
  `revogado_em` datetime DEFAULT NULL,
  `revogado_por` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_aps_pu_usuario` (`usuario_id`),
  KEY `ix_aps_pu_nivel_divisao` (`nivel_id`,`divisao_id`),
  KEY `fk_aps_pu_divisao` (`divisao_id`),
  KEY `fk_aps_pu_concedido` (`concedido_por`),
  KEY `fk_aps_pu_revogado` (`revogado_por`),
  CONSTRAINT `fk_aps_pu_concedido` FOREIGN KEY (`concedido_por`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_aps_pu_divisao` FOREIGN KEY (`divisao_id`) REFERENCES `divisoes` (`id`),
  CONSTRAINT `fk_aps_pu_nivel` FOREIGN KEY (`nivel_id`) REFERENCES `niveis_acesso` (`id`),
  CONSTRAINT `fk_aps_pu_revogado` FOREIGN KEY (`revogado_por`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_aps_pu_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `chk_aps_pu_expiracao` CHECK (((`expira_em` is null) or (`expira_em` > `concedido_em`)))
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissoes_usuarios`
--

LOCK TABLES `permissoes_usuarios` WRITE;
/*!40000 ALTER TABLE `permissoes_usuarios` DISABLE KEYS */;
INSERT INTO `permissoes_usuarios` VALUES (1,6,1,NULL,NULL,'2026-10-24 12:22:37',NULL,NULL,NULL),(2,7,1,NULL,NULL,'2026-10-24 12:22:38',NULL,NULL,NULL),(3,27,2,NULL,NULL,'2026-10-24 12:48:51',NULL,NULL,NULL),(4,28,3,NULL,NULL,'2026-10-24 12:48:51',NULL,NULL,NULL);
/*!40000 ALTER TABLE `permissoes_usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recursos_protegidos`
--

DROP TABLE IF EXISTS `recursos_protegidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recursos_protegidos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) NOT NULL,
  `descricao` text,
  `conteudo` text NOT NULL,
  `nivel_exigido_id` int NOT NULL,
  `divisao_id` int DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `criado_por` int DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `atualizado_em` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_aps_recurso_nivel` (`nivel_exigido_id`),
  KEY `ix_aps_recurso_divisao` (`divisao_id`),
  KEY `fk_aps_recurso_autor` (`criado_por`),
  CONSTRAINT `fk_aps_recurso_autor` FOREIGN KEY (`criado_por`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_aps_recurso_divisao` FOREIGN KEY (`divisao_id`) REFERENCES `divisoes` (`id`),
  CONSTRAINT `fk_aps_recurso_nivel` FOREIGN KEY (`nivel_exigido_id`) REFERENCES `niveis_acesso` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recursos_protegidos`
--

LOCK TABLES `recursos_protegidos` WRITE;
/*!40000 ALTER TABLE `recursos_protegidos` DISABLE KEYS */;
INSERT INTO `recursos_protegidos` VALUES (1,'Informacao Geral','Informacao basica do sistema','Conteudo de teste para o nivel geral',1,NULL,1,NULL,'2026-10-28 15:42:11',NULL),(2,'Relatorio da Diretoria','Informacao destinada aos diretores','Conteudo ficticio restrito a diretoria',2,NULL,1,NULL,'2026-10-28 15:42:11',NULL),(3,'Relatorio Ministerial','Informacao restrita ao ministro','Conteudo ficticio confidencial',3,NULL,1,NULL,'2026-10-28 15:42:11',NULL);
/*!40000 ALTER TABLE `recursos_protegidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regras_acesso`
--

DROP TABLE IF EXISTS `regras_acesso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regras_acesso` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nivel_permissao` int NOT NULL,
  `tipo_informacao` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nivel_permissao` (`nivel_permissao`,`tipo_informacao`),
  CONSTRAINT `fk_regras_acesso_permissoes` FOREIGN KEY (`nivel_permissao`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regras_acesso`
--

LOCK TABLES `regras_acesso` WRITE;
/*!40000 ALTER TABLE `regras_acesso` DISABLE KEYS */;
INSERT INTO `regras_acesso` VALUES (1,1,'Geral','Acesso as informacoes basicas do sistema'),(2,2,'Geral','Acesso as informacoes gerais'),(3,2,'Diretoria','Acesso as informacoes adicionais dos diretores'),(4,3,'Geral','Acesso a todas as informacoes gerais'),(5,3,'Diretoria','Acesso as informacoes destinadas aos diretores'),(6,3,'Ministro','Acesso as informacoes exclusivas do Ministro');
/*!40000 ALTER TABLE `regras_acesso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tentativas_acesso`
--

DROP TABLE IF EXISTS `tentativas_acesso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tentativas_acesso` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `data_hora` datetime DEFAULT CURRENT_TIMESTAMP,
  `resultado` enum('AUTORIZADO','NEGADO') NOT NULL,
  `motivo` varchar(255) DEFAULT NULL,
  `requisicao_id` varchar(36) NOT NULL,
  `conta_solicitante_id` int DEFAULT NULL,
  `usuario_candidato_id` int DEFAULT NULL,
  `recurso_id` int DEFAULT NULL,
  `configuracao_id` int DEFAULT NULL,
  `status_processamento` varchar(40) DEFAULT NULL,
  `status_reconhecimento` varchar(40) DEFAULT NULL,
  `similaridade` double DEFAULT NULL,
  `limiar_aplicado` double DEFAULT NULL,
  `margem_aplicada` double DEFAULT NULL,
  `acesso_permitido` tinyint(1) NOT NULL,
  `origem` varchar(50) DEFAULT NULL,
  `tempo_total_ms` double DEFAULT NULL,
  `ocorrido_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_aps_requisicao` (`requisicao_id`),
  KEY `usuario_id` (`usuario_id`),
  KEY `ix_aps_tentativa_data` (`ocorrido_em`),
  KEY `ix_aps_tentativa_usuario` (`usuario_candidato_id`,`ocorrido_em`),
  KEY `fk_aps_tentativa_conta` (`conta_solicitante_id`),
  KEY `fk_aps_tentativa_recurso` (`recurso_id`),
  KEY `fk_aps_tentativa_config` (`configuracao_id`),
  CONSTRAINT `fk_aps_tentativa_config` FOREIGN KEY (`configuracao_id`) REFERENCES `configuracoes_biometricas` (`id`),
  CONSTRAINT `fk_aps_tentativa_conta` FOREIGN KEY (`conta_solicitante_id`) REFERENCES `contas` (`id`),
  CONSTRAINT `fk_aps_tentativa_recurso` FOREIGN KEY (`recurso_id`) REFERENCES `recursos_protegidos` (`id`),
  CONSTRAINT `fk_aps_tentativa_usuario` FOREIGN KEY (`usuario_candidato_id`) REFERENCES `usuarios` (`id`),
  CONSTRAINT `tentativas_acesso_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tentativas_acesso`
--

LOCK TABLES `tentativas_acesso` WRITE;
/*!40000 ALTER TABLE `tentativas_acesso` DISABLE KEYS */;
INSERT INTO `tentativas_acesso` VALUES (1,6,'2026-10-24 12:41:50','NEGADO','Teste: usuario sem nivel exigido','72c508a9-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 12:41:50'),(2,6,'2026-10-24 12:41:50','AUTORIZADO','Teste: simulacao de acesso autorizado','72c512b4-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 12:41:50'),(3,6,'2026-10-24 12:41:55','NEGADO','Teste: usuario sem nivel exigido','72c514fa-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 12:41:55'),(4,6,'2026-10-24 12:41:55','AUTORIZADO','Teste: simulacao de acesso autorizado','72c5167a-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 12:41:55'),(5,6,'2026-10-24 12:42:13','NEGADO','Teste: usuario sem nivel exigido','72c51895-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 12:42:13'),(6,6,'2026-10-24 12:42:13','AUTORIZADO','Teste: simulacao de acesso autorizado','72c51a2a-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 12:42:13'),(7,6,'2026-10-24 15:59:33','NEGADO','Nivel insuficiente para a area solicitada','72c51be0-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:33'),(8,7,'2026-10-24 15:59:33','NEGADO','Nivel insuficiente para a area solicitada','72c51da8-d47b-11f1-897d-00e2697b9e11',NULL,7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:33'),(9,27,'2026-10-24 15:59:33','NEGADO','Nivel insuficiente para a area solicitada','72c51f3c-d47b-11f1-897d-00e2697b9e11',NULL,27,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:33'),(10,28,'2026-10-24 15:59:33','AUTORIZADO','Teste de acesso a area exclusiva do ministro','72c520c2-d47b-11f1-897d-00e2697b9e11',NULL,28,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 15:59:33'),(14,6,'2026-10-24 15:59:48','NEGADO','Nivel insuficiente para a area solicitada','72c52255-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:48'),(15,7,'2026-10-24 15:59:48','NEGADO','Nivel insuficiente para a area solicitada','72c523c4-d47b-11f1-897d-00e2697b9e11',NULL,7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:48'),(16,27,'2026-10-24 15:59:48','NEGADO','Nivel insuficiente para a area solicitada','72c52528-d47b-11f1-897d-00e2697b9e11',NULL,27,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 15:59:48'),(17,28,'2026-10-24 15:59:48','AUTORIZADO','Teste de acesso a area exclusiva do ministro','72c52656-d47b-11f1-897d-00e2697b9e11',NULL,28,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 15:59:48'),(21,6,'2026-10-24 16:01:09','NEGADO','Nivel insuficiente para a area solicitada','72c52799-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:09'),(22,7,'2026-10-24 16:01:09','NEGADO','Nivel insuficiente para a area solicitada','72c528f3-d47b-11f1-897d-00e2697b9e11',NULL,7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:09'),(23,27,'2026-10-24 16:01:09','NEGADO','Nivel insuficiente para a area solicitada','72c529f9-d47b-11f1-897d-00e2697b9e11',NULL,27,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:09'),(24,28,'2026-10-24 16:01:09','AUTORIZADO','Teste de acesso a area exclusiva do ministro','72c52adf-d47b-11f1-897d-00e2697b9e11',NULL,28,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 16:01:09'),(28,6,'2026-10-24 16:01:53','NEGADO','Nivel insuficiente para a area solicitada','72c52bcb-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:53'),(29,7,'2026-10-24 16:01:53','NEGADO','Nivel insuficiente para a area solicitada','72c52d82-d47b-11f1-897d-00e2697b9e11',NULL,7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:53'),(30,27,'2026-10-24 16:01:53','NEGADO','Nivel insuficiente para a area solicitada','72c52eb7-d47b-11f1-897d-00e2697b9e11',NULL,27,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-24 16:01:53'),(31,28,'2026-10-24 16:01:53','AUTORIZADO','Teste de acesso a area exclusiva do ministro','72c53011-d47b-11f1-897d-00e2697b9e11',NULL,28,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-24 16:01:53'),(32,6,'2026-10-27 11:16:13','NEGADO','Teste: usuario sem nivel exigido','72c53164-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-27 11:16:13'),(33,6,'2026-10-27 11:16:13','AUTORIZADO','Teste: simulacao de acesso autorizado','72c53265-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-27 11:16:13'),(34,6,'2026-10-27 11:16:37','NEGADO','Teste: usuario sem nivel exigido','72c53357-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,'LEGADO',NULL,'2026-10-27 11:16:37'),(35,6,'2026-10-27 11:16:37','AUTORIZADO','Teste: simulacao de acesso autorizado','72c5343e-d47b-11f1-897d-00e2697b9e11',NULL,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1,'LEGADO',NULL,'2026-10-27 11:16:37');
/*!40000 ALTER TABLE `tentativas_acesso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `cpf` varchar(14) NOT NULL,
  `login` varchar(50) NOT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `nivel_permissao` int NOT NULL,
  `status` enum('ativo','inativo') DEFAULT 'ativo',
  `data_cadastro` datetime DEFAULT CURRENT_TIMESTAMP,
  `matricula` varchar(50) DEFAULT NULL,
  `email` varchar(254) DEFAULT NULL,
  `divisao_id` int DEFAULT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT '1',
  `criado_por` int DEFAULT NULL,
  `criado_em` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `atualizado_em` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cpf` (`cpf`),
  UNIQUE KEY `login` (`login`),
  UNIQUE KEY `uq_usuarios_matricula` (`matricula`),
  UNIQUE KEY `uq_usuarios_email` (`email`),
  KEY `fk_usuarios_permissoes` (`nivel_permissao`),
  KEY `ix_usuarios_divisao` (`divisao_id`),
  KEY `fk_usuarios_criado_por` (`criado_por`),
  CONSTRAINT `fk_usuarios_criado_por` FOREIGN KEY (`criado_por`) REFERENCES `contas` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_usuarios_divisao` FOREIGN KEY (`divisao_id`) REFERENCES `divisoes` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_usuarios_permissoes` FOREIGN KEY (`nivel_permissao`) REFERENCES `permissoes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (6,'João da Silva','123.456.789-00','joao','hash_da_senha',1,'ativo','2026-10-24 12:22:37',NULL,NULL,NULL,NULL,1,NULL,'2026-10-24 12:22:37',NULL),(7,'Usuario Teste','000.000.000-00','teste_nivel1','HASH_DE_TESTE_NAO_USAR',1,'ativo','2026-10-24 12:22:38',NULL,NULL,NULL,NULL,1,NULL,'2026-10-24 12:22:38',NULL),(27,'Diretor Teste','000.000.000-01','diretor_teste','HASH_FICTICIO',2,'ativo','2026-10-24 12:48:51',NULL,NULL,NULL,NULL,1,NULL,'2026-10-24 12:48:51',NULL),(28,'Ministro Teste','000.000.000-02','ministro_teste','HASH_FICTICIO',3,'ativo','2026-10-24 12:48:51',NULL,NULL,NULL,NULL,1,NULL,'2026-10-24 12:48:51',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-30 15:42:42

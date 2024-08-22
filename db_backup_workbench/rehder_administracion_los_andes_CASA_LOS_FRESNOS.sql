-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: mysql.50webs.com    Database: rehder_administracion_los_andes
-- ------------------------------------------------------
-- Server version	5.7.23

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
-- Table structure for table `CASA_LOS_FRESNOS`
--

DROP TABLE IF EXISTS `CASA_LOS_FRESNOS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CASA_LOS_FRESNOS` (
  `articulo` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `precio` decimal(12,2) DEFAULT NULL,
  `art_descripcion` text COLLATE utf8_unicode_ci,
  `imagen` longblob,
  `speech` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `descripcion` text COLLATE utf8_unicode_ci,
  `pregunta` text COLLATE utf8_unicode_ci,
  UNIQUE KEY `articulo` (`articulo`),
  UNIQUE KEY `speech` (`speech`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CASA_LOS_FRESNOS`
--

LOCK TABLES `CASA_LOS_FRESNOS` WRITE;
/*!40000 ALTER TABLE `CASA_LOS_FRESNOS` DISABLE KEYS */;
INSERT INTO `CASA_LOS_FRESNOS` VALUES (NULL,NULL,NULL,NULL,'PRECIO Y FINANCIACION','en 275,000 se financia con 65,000 de enganche a 30 años y en cash se puede mejorar el\r\nPrecio de 275,000, interés del %9.5 anual\r\n\r\n',NULL),(NULL,NULL,NULL,NULL,'NUMERO JOSE','1 (956) 559-0753\r\nDE PREFERENCIA LLAMAR',NULL),('CALLE HERMOSA, LOS FRESNOS',275000.00,'ha sido remodelada recientemente\r\ntiene cerca de madera\r\n1,985 pies de la pura casa\r\n1 cuatro de acre es el lote\r\ntiene porque en la entrada donde se puede estacionar 1 carro\r\nvista al lago\r\nParte de abajo\r\n2 recámaras, \r\n2 baños, sala cocina,\r\n cuarto de lavandería, a/c central, \r\n\r\nparte de arriba una recámara, sala cocina, baño con mini split, \r\nDIRECCION: DIRECCIÓN: 30900 Calle hermosa los Fresnos',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `CASA_LOS_FRESNOS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-01  9:19:35

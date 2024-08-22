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
-- Table structure for table `MANUEL_INGRAM`
--

DROP TABLE IF EXISTS `MANUEL_INGRAM`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MANUEL_INGRAM` (
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
-- Dumping data for table `MANUEL_INGRAM`
--

LOCK TABLES `MANUEL_INGRAM` WRITE;
/*!40000 ALTER TABLE `MANUEL_INGRAM` DISABLE KEYS */;
INSERT INTO `MANUEL_INGRAM` VALUES ('TERRENO',299.00,'direccion: 1254 w us hwy 77, San Benito\r\ncoordenadas: 26.14926148442584, -97.64146978201762\r\n- 100 x 130 pies.\r\n- 10.000 área en concreto.\r\n13 mil pies cuadrados\r\n-INCLUYE casa oficina con baño\r\n   140 pies.\r\n- Garaje para 4 vehículos.\r\n- 1 compresor.\r\n- 1 maquina para quitar llanta.\r\n- 1 maquina para balancear llanta.\r\n actualmente es un taller mecánico\r\n (pago al contado)',NULL,NULL,NULL,NULL),('GROSERY STORE',499.00,'449 Ratliff Rd, San Benito, TX 78586, EE. UU.\r\ntienda funcionando al 100\r\ntodo incluido \r\nheladera de 7 puertas\r\nestantes \r\ny productos\r\n2400 píes\r\n\r\n+ CASA  2 RECAMARAS 1 BAÑO (ACTUALEMTE EN RENTA)\r\n\r\n',NULL,NULL,NULL,NULL),(NULL,NULL,NULL,NULL,'DISPONIBILIDAD HORARIA','7am a 7pm  de lunes a sabados\r\nPUEDE LLAMAR A LOS INTERSADOS Y CORDINAR CON ELLOS\r\nSI NO PODEMOS AGENDARLE UNA CITA DIRECTAMENTE\r\n',NULL),(NULL,NULL,NULL,NULL,'CONTACTO MANUEL ','LLAMAR/ MENSAJES SIEMPRE A WHATSAPP\r\n(956) 592-7032',NULL);
/*!40000 ALTER TABLE `MANUEL_INGRAM` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-01  9:19:25

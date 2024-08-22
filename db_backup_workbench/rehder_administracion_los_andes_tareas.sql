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
-- Table structure for table `tareas`
--

DROP TABLE IF EXISTS `tareas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tareas` (
  `idtarea` tinyint(4) NOT NULL AUTO_INCREMENT,
  `tarea` tinytext COLLATE utf8_unicode_ci NOT NULL,
  `color` varchar(6) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`idtarea`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tareas`
--

LOCK TABLES `tareas` WRITE;
/*!40000 ALTER TABLE `tareas` DISABLE KEYS */;
INSERT INTO `tareas` VALUES (0,'','FFFFFF'),(1,'NO ATENDIÓ','D5D8DC'),(2,'NO LE INTERESA','F44336'),(3,'CITA PROGRAMADA','00FFFF'),(4,'NO PUDO ASISTIR','EDBB99'),(5,'SI ASISTIÓ','85C1E9'),(6,'REALIZÓ APLICACIÓN','D2B4DE'),(7,'RENTÓ','00FF00'),(8,'LLAMAR','FFFF00'),(9,'SEGUIMIENTO 1','E6B0AA'),(10,'SEGUIMIENTO 2','D98880'),(11,'SEGUIMIENTO 3','C0392B'),(12,'ESPERAR LLAMADA','E67E22'),(13,'INFORMACIÓN ENVIADA','AED6F1'),(14,'INSPECCIÓN PROGRAMADA','48C9B0'),(15,'INSPECCIÓN REALIZADA','82E0AA'),(16,'HACER COTIZACIÓN','D0ECE7'),(17,'COTIZACIÓN ENVIADA','A9CCE3'),(18,'INSTALACIÓN PROGRAMADA','2ECC71'),(19,'YA INSTALÓ','00FF00'),(20,'SEGUIMIENTO DE PAGO','ECE0F8'),(21,'SOPORTE TÉCNICO','A9E2F3'),(22,'SEGUIMIENTO DE SERVICIO','DAF7A6'),(23,'SE VENDE SERVICIO','A3E4D7'),(24,'TAREA REALIZADA','00FF00'),(25,'CHECK-IN','D4E6F1'),(26,'CHECK-OUT','D7BDE2'),(27,'RESERVÓ','00FF00');
/*!40000 ALTER TABLE `tareas` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-01  9:20:30

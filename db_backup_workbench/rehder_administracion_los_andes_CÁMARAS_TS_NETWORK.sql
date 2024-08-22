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
-- Table structure for table `C�MARAS_TS_NETWORK`
--

DROP TABLE IF EXISTS `C�MARAS_TS_NETWORK`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CÁMARAS_TS_NETWORK` (
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
-- Dumping data for table `C�MARAS_TS_NETWORK`
--

LOCK TABLES `C�MARAS_TS_NETWORK` WRITE;
/*!40000 ALTER TABLE `C�MARAS_TS_NETWORK` DISABLE KEYS */;
INSERT INTO `C�MARAS_TS_NETWORK` VALUES (NULL,NULL,NULL,NULL,NULL,NULL,'¿TIENE ÁTICO?'),(NULL,NULL,NULL,NULL,NULL,NULL,'¿DE CUANTOS PIES ES SU CASA?'),(NULL,NULL,NULL,NULL,NULL,NULL,'¿DE QUE MATERIAL ES LA CONSTRUCCIÓN?'),(NULL,NULL,NULL,NULL,NULL,NULL,'¿LA INSULACIÓN TIENE FOAM?'),(NULL,NULL,NULL,NULL,'VENTA DE CAMARAS ','Hola muy buenos días, mi nombre es………. de la empresa de cámaras de seguridad TS-Network. \r\nCómo le va?\r\n Cómo le indiqué somos una empresa de cámaras de seguridad ubicada aquí en Brownsville nuestra oficina está en 847 N Expressway, tenemos disponibilidad de trabajar en todo el valle, estamos ofreciendo nuestro servicio de Cámaras de seguridad para hogares y negocios. \r\nActualmente cuenta con un servicio de cámaras de seguridad?  \r\n•	Si dice que si: Estaría interesado en tener un mejor servicio o tener un mantenimiento de su servicio de cámaras? Sus cámaras trabajan correctamente? \r\nSomos un servicio de cámaras de seguridad que tiene más de diez años de experiencia.\r\nCon el servicio de mantenimiento ofrecemos una limpieza, verificación de funcionamiento.\r\n\r\n•	Si dice que no: Contamos con una promoción de Servicio de cámaras.. Kits de  4, 8 y 16 cámaras ip 5 MP.-\r\no	Cámaras con visualización remota desde una app del teléfono.\r\no	Visión nocturna y grabación por detección de movimiento o 24 hs , Audio . \r\n•	Cotización: 750 dólares de contado con posible financiación, un enganche del 50 % y el resto en pagos. Si es en pagos la modalidad seria la siguiente, se le incrementa al 50 % restante un interés del 10 %  por mes sobre el total de la deuda. Este costo esta sujeto a una inspección previa del lugar donde se colocarán las cámaras, esta inspección es sin costo.  \r\n•	Existe la posibilidad de hacer una visita técnica, si nos permite, con nuestro técnico para evaluar cuántas cámaras necesita y darle una cotización. \r\n•	Tiene alguna duda con respecto a la información brindada?\r\n•	Quiere que le enviemos una cotización por escrito?, ok perfecto puede proporcionarme su email, Gracias\r\n•	Quedamos atento a su respuesta, Mi nombre es---------- que tenga excelente dia!\r\n',NULL),('KIT DE 4 CAMARAS ',750.00,'4 cámaras IP 5MP - HD excelente calidad de video,\r\nvisión nocturna\r\nAudio\r\nGrabación por detección de movimiento o 24 hs \r\nCableadas\r\n\r\nAcceso remoto desde su teléfono o tablet desde cualquier punto del mundo.\r\n',NULL,NULL,NULL,NULL),('KIT DE 16 CAMARAS',2600.00,'16 cámaras IP 5MP - HD excelente calidad de video,\r\nvisión nocturna\r\nAudio\r\nGrabación por detección de movimiento o 24 hs \r\nCableadas\r\n\r\nAcceso remoto desde su teléfono o tablet desde cualquier punto del mundo.\r\n',NULL,NULL,NULL,NULL),('KIT DE 8 CAMARAS ',1500.00,'8 cámaras IP 5MP - HD excelente calidad de video,\r\nvisión nocturna\r\nAudio\r\nGrabación por detección de movimiento o 24 hs \r\nCableadas\r\n\r\nAcceso remoto desde su teléfono o tablet desde cualquier punto del mundo.\r\n',NULL,NULL,NULL,NULL),('KIT DE 4 CAMARAS 2MP SIN AUDIO',395.00,'4 cámaras  2MP  buena calidad de video,\r\nvisión nocturna\r\nGrabación por detección de movimiento o 24 hs\r\nCableadas\r\nAcceso remoto desde su teléfono o tablet desde cualquier punto del mundo.',NULL,NULL,NULL,NULL),('KIT DE 4 CAMARAS 5MP SIN AUDIO ',600.00,'4 cámaras IP 5MP - HD excelente calidad de video,\r\nvisión nocturna\r\n\r\nGrabación por detección de movimiento o 24 hs\r\nCableadas\r\nAcceso remoto desde su teléfono o tablet desde cualquier punto del mundo.\r\n',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `C�MARAS_TS_NETWORK` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-01  9:20:45

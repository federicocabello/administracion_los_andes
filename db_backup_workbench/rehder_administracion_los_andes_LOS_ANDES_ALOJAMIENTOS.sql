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
-- Table structure for table `LOS_ANDES_ALOJAMIENTOS`
--

DROP TABLE IF EXISTS `LOS_ANDES_ALOJAMIENTOS`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `LOS_ANDES_ALOJAMIENTOS` (
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
-- Dumping data for table `LOS_ANDES_ALOJAMIENTOS`
--

LOCK TABLES `LOS_ANDES_ALOJAMIENTOS` WRITE;
/*!40000 ALTER TABLE `LOS_ANDES_ALOJAMIENTOS` DISABLE KEYS */;
INSERT INTO `LOS_ANDES_ALOJAMIENTOS` VALUES (NULL,NULL,NULL,NULL,'CUANDO ES EL DIA DE SU CHECK OUT','SI SE RETIRA TEMPRANO POR LA MAÑANA:\r\nse le manda por temprano el siguiente mensaje: \r\n\r\nMuy buenos días (nombre del huésped), como se encuentra hoy? solo para saber como ha sido su experiencia descansando anoche? si hay algo que necesite por favor nos avisa! muchas gracias!\r\n\r\nSI AUN NO HA SALIDO DE LA CASA: \r\n\r\nMuy buenos días (nombre del huésped), como se encuentra hoy? le recordamos que la hora de check out es a las 10 am, si llega a necesitar mas tiempo para salir o desea extender su estadia avísenos lo antes posible. recuerde que estamos aquí para servirle!',NULL),(NULL,NULL,NULL,NULL,'SI SE REQUIERE MODIFICAR UNA RESERVA POR EL HUESPED','(DESDE EL CELULAR)\r\nToca Perfil  y luego Usar como anfitrión .\r\nToca Reservaciones.\r\nToca Próximas y selecciona la que quieras modificar.\r\nToca Detalles y luego Modificar reservación.\r\nCambia (lo que se requiera) el anuncio, las fechas, el número de huéspedes o el precio.\r\nRevisa los cambios y toca Enviar solicitud.\r\n(DESDE LA COMPUTADORA)\r\nHaz clic en Hoy > Reservaciones.\r\nHaz clic en Próximas y selecciona la que quieras modificar.\r\nEntra en Detalles y, a continuación, haz clic en Modificar la reservación.\r\nCambia (Lo que se requiera) el anuncio, las fechas, el número de huéspedes o el precio.\r\nRevisa los cambios y luego haz clic en Enviar solicitud.',NULL),(NULL,NULL,NULL,NULL,'MENSAJE FINAL DE EVALUACION AL HUESPED ','Hola (nombre del Huesped) Fue un placer recibirlo en nuestra casa. Espero que hayan disfrutado su estadía y que hayan tenido una experiencia excelente y confortable.\r\n\r\nApreciaríamos que se pueda tomar 60 segundos para darnos una reseña de 5 estrellas para que otros puedan disfrutar de nuestra casa como usted!\r\n\r\nSaludos, Los Andes Alojamientos \r\n',NULL),(NULL,NULL,NULL,NULL,'CUANDO ES EL DIA DE SU CHECK IN','SI LA RESERVA ES POR AIRBNB:\r\nSe le manda en el momento de su reserva el siguiente mensaje:\r\nMuy buenos días/ tardes, como se encuentra el día de hoy? A que hora estima su llegada?\r\ntambién solo le recordamos que pueda leer atentamente las instrucciones por favor, y si ha algo que necesite nos avisa. Muchas gracias! \r\n\r\nSI LA RESERVA ES POR BOOKING:\r\nMuy buenos días/ tardes, como esta el día de hoy?  a que hora estima s llegada?\r\nsu cuarto es el numero (.......tanto......) solo le recordamos que pueda leer atentamente las instrucciones por favor,  y si ha algo que necesite nos avisa. Muchas gracias! ',NULL),(NULL,NULL,NULL,NULL,'ZELLE LOS ANDES ','zelle@losandestx.com',NULL),(NULL,NULL,NULL,NULL,'MENSAJE CORDIAL','Hola ( nombre de la persona) \r\nmuchas gracias por elegirnos como parte de tu próximo viaje. nos sentimos honrados de tener la oportunidad de hospedarte y servirte.\r\nla informacion del alojamiento se le enviaran el día de la reserva.\r\nsaludos \r\nLos Andes Alojamientos  ',NULL),(NULL,NULL,NULL,NULL,'NUMERO SANDRA (LIMPIEZA)','956 455 5290',NULL),(NULL,NULL,NULL,NULL,'MENSAJE PARA PAGOS SAN RAFAEL','Querido Huésped, le agradecemos por elegirnos como la mejor opción para su estadía. Queremos resaltarle un punto importante para nosotros como lo es la modalidad de pago para sus reservas, la cual por políticas internas de la empresa se efectuará de la siguiente manera, la trasferencia se realizará a la siguiente cuenta:\r\n\r\nMERCADO PAGO\r\n\r\nLucas Martin Rehder\r\nCVU: 0000003100041829933515\r\nAlias: lucas.003.eter.mp\r\n\r\nla cual deberás enviar soporte para poder validar el estado y monto cancelado. Estamos en el deber de informarte si esta fue recibida. De no compartir este soporte en un lapso de un (1) día la reserva se cancelará automáticamente.',NULL);
/*!40000 ALTER TABLE `LOS_ANDES_ALOJAMIENTOS` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-08-01  9:20:42

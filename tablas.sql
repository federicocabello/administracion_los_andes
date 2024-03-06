CREATE TABLE `altacliente` (
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

CREATE TABLE `auth` (
 `user` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
 `password` varchar(32) COLLATE utf8_unicode_ci NOT NULL,
 `fullname` tinytext COLLATE utf8_unicode_ci,
 `rol` varchar(5) COLLATE utf8_unicode_ci NOT NULL,
 PRIMARY KEY (`user`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `calendario` (
 `date` date NOT NULL,
 `date_format` tinytext COLLATE utf8_unicode_ci
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `clientes` (
 `empresa` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
 `logo` longblob,
 `nombre` tinytext COLLATE utf8_unicode_ci,
 `direccion` tinytext COLLATE utf8_unicode_ci,
 `telefono` tinytext COLLATE utf8_unicode_ci,
 `email` tinytext COLLATE utf8_unicode_ci,
 `vende` text COLLATE utf8_unicode_ci,
 `plan` tinyint(4) DEFAULT NULL,
 `plan_fichainterna` text COLLATE utf8_unicode_ci,
 `fecha` date DEFAULT NULL,
 `contrato` longblob,
 UNIQUE KEY `empresa` (`empresa`),
 KEY `plan` (`plan`),
 CONSTRAINT `fk_plan` FOREIGN KEY (`plan`) REFERENCES `planes` (`idplan`) ON DELETE CASCADE ON UPDATE CASCADE
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `movimientos` (
 `n_mov` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
 `mov` text COLLATE utf8_unicode_ci NOT NULL,
 `date_mov` datetime NOT NULL,
 PRIMARY KEY (`n_mov`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB AUTO_INCREMENT=215 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `planes` (
 `idplan` tinyint(4) NOT NULL AUTO_INCREMENT,
 `plan` tinytext COLLATE utf8_unicode_ci NOT NULL,
 `descripcion` text COLLATE utf8_unicode_ci,
 `precio` decimal(12,2) DEFAULT '0.00',
 PRIMARY KEY (`idplan`),
 KEY `idplan` (`idplan`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

CREATE TABLE `registros` (
 `empresa` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
 `agente` tinytext COLLATE utf8_unicode_ci,
 `nombre` tinytext COLLATE utf8_unicode_ci,
 `telefono` tinytext COLLATE utf8_unicode_ci,
 `direccion` tinytext COLLATE utf8_unicode_ci,
 `email` tinytext COLLATE utf8_unicode_ci,
 `motivo` text COLLATE utf8_unicode_ci,
 `cotizacion` text COLLATE utf8_unicode_ci,
 `cotizaciontotal` decimal(12,2) DEFAULT '0.00',
 `fecha` datetime NOT NULL,
 `tarea` tinyint(4) DEFAULT NULL,
 `fecha_tarea` date DEFAULT NULL,
 `hora_tarea` varchar(7) COLLATE utf8_unicode_ci DEFAULT NULL,
 `estado` varchar(9) COLLATE utf8_unicode_ci NOT NULL,
 `nota_rechazo` text COLLATE utf8_unicode_ci,
 `pregunta` text COLLATE utf8_unicode_ci,
 `respuesta` text COLLATE utf8_unicode_ci,
 KEY `fk_tarea` (`tarea`),
 CONSTRAINT `fk_tarea` FOREIGN KEY (`tarea`) REFERENCES `tareas` (`idtarea`) ON DELETE CASCADE ON UPDATE CASCADE
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
CREATE TABLE `tareas` (
 `idtarea` tinyint(4) NOT NULL AUTO_INCREMENT,
 `tarea` tinytext COLLATE utf8_unicode_ci NOT NULL,
 PRIMARY KEY (`idtarea`)
) /*!50100 TABLESPACE `rehder_administracion_los_andes` */ ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
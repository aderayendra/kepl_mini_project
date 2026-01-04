-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Jan 04, 2026 at 01:24 AM
-- Server version: 10.11.13-MariaDB
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `kepl_siakad`
--

-- --------------------------------------------------------

--
-- Table structure for table `mahasiswa`
--

CREATE TABLE `mahasiswa` (
  `nim` bigint(20) NOT NULL,
  `password` varchar(64) NOT NULL,
  `nama` varchar(100) NOT NULL,
  `jenis_kelamin` enum('laki-laki','perempuan') NOT NULL,
  `jurusan` varchar(200) NOT NULL,
  `prodi` varchar(200) NOT NULL,
  `tanggal_masuk` date NOT NULL,
  `no_hp` varchar(16) NOT NULL,
  `alamat` varchar(300) NOT NULL,
  `agama` varchar(50) NOT NULL,
  `nik` varchar(16) NOT NULL,
  `nomor_kk` varchar(16) NOT NULL,
  `nama_ayah` varchar(100) NOT NULL,
  `nama_ibu` varchar(100) NOT NULL,
  `waktu_login` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `mahasiswa`
--

INSERT INTO `mahasiswa` VALUES
(2024000001,'29a935e0c33cc70ee121548f15a201320f1af28d7eb323fefdafbae9cd945a4e','Eko Hidayat','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081254582631','Jl. Pendidikan No. 1, Kota Pelajar','Kristen','3201172649673879','3201104444423731','Ayah Eko Hidayat','Ibu Eko Hidayat',NULL),
(2024000002,'c19382aa01a213fa9f49336c4440d338cb3e81d4e0039b0ee5d65ca6dd52a020','Putri Kurniawan','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081255834079','Jl. Pendidikan No. 2, Kota Pelajar','Budha','3201598097602025','3201500315783070','Ayah Putri Kurniawan','Ibu Putri Kurniawan',NULL),
(2024000003,'7f334407ecb2465c59bf1826e99ae42940ff9aae72f54dc5e18b706384d0b941','Dewi Santoso','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081271316993','Jl. Pendidikan No. 3, Kota Pelajar','Budha','3201547130404779','3201475747209413','Ayah Dewi Santoso','Ibu Dewi Santoso',NULL),
(2024000004,'a39c22ab7007466384b3930a560e4407dfb5ca30804f222442fb9099961661be','Wati Prasetyo','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081267737166','Jl. Pendidikan No. 4, Kota Pelajar','Katolik','3201147978060221','3201809467731521','Ayah Wati Prasetyo','Ibu Wati Prasetyo',NULL),
(2024000005,'631b3b68acfb93d7a816f693fc55ca913bbf04859ed1d6ff247899c864e10c2e','Sari Susilo','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081244220387','Jl. Pendidikan No. 5, Kota Pelajar','Budha','3201764397175216','3201593979370702','Ayah Sari Susilo','Ibu Sari Susilo',NULL),
(2024000006,'c3ae3729416a176a6a7d42dabe2f4ca177248999f132013e2be305f0cb68110b','Dewi Kurniawan','perempuan','Ekonomi','Akuntansi','2024-08-01','081226384662','Jl. Pendidikan No. 6, Kota Pelajar','Budha','3201983880649890','3201208310987464','Ayah Dewi Kurniawan','Ibu Dewi Kurniawan',NULL),
(2024000007,'db88c6e5faa95bb52d4a2ea77140cf80b6ec58092ec43058b959ae93b3dbc413','Maya Saputra','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081265534698','Jl. Pendidikan No. 7, Kota Pelajar','Katolik','3201548502998063','3201576371485495','Ayah Maya Saputra','Ibu Maya Saputra',NULL),
(2024000008,'15be659bcb342dadd3f6bbb5777dc8c07f28fcaea4be816bf4f9c9eef20a0853','Hendra Utomo','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081265321524','Jl. Pendidikan No. 8, Kota Pelajar','Konghucu','3201990324504694','3201971529720783','Ayah Hendra Utomo','Ibu Hendra Utomo',NULL),
(2024000009,'03751fd5ecfa301f1a5170b76a30bd34f1225c71d062d40090a45bc16623f276','Budi Kurniawan','laki-laki','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081278385764','Jl. Pendidikan No. 9, Kota Pelajar','Islam','3201641429457356','3201297561686137','Ayah Budi Kurniawan','Ibu Budi Kurniawan',NULL),
(2024000010,'fac99d96a62f13ba37f4dec05170fe62ba29df6d813bf015783c17b054e117e4','Andi Santoso','laki-laki','Teknologi Informasi','Teknik Informatika','2024-08-01','081257653253','Jl. Pendidikan No. 10, Kota Pelajar','Budha','3201804680900773','3201866161802119','Ayah Andi Santoso','Ibu Andi Santoso',NULL),
(2024000011,'d1f84d6c29bbec162b4ba71e1f7890d84cf531f471ef07827291df1771f1cb90','Siti Saputra','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081245397951','Jl. Pendidikan No. 11, Kota Pelajar','Konghucu','3201808203193238','3201955928280530','Ayah Siti Saputra','Ibu Siti Saputra',NULL),
(2024000012,'da72f1a1e3593d92952e9fa9e57c54539f9454b8592ecf903dec61ad7b461012','Wati Saputra','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081224675407','Jl. Pendidikan No. 12, Kota Pelajar','Konghucu','3201279200673395','3201198892488128','Ayah Wati Saputra','Ibu Wati Saputra',NULL),
(2024000013,'601d802fe4d32b892937ec7ec0d60a5d7bec312d7e1b21a81a40b8f2157b204c','Maya Prasetyo','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081299053187','Jl. Pendidikan No. 13, Kota Pelajar','Islam','3201476686146424','3201623749221988','Ayah Maya Prasetyo','Ibu Maya Prasetyo',NULL),
(2024000014,'008d5b6c51cdf7ff0368df86f8fb322749ac8e76675fb2d847a146147ff44267','Siti Nugroho','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081236863479','Jl. Pendidikan No. 14, Kota Pelajar','Katolik','3201528050161408','3201997916850319','Ayah Siti Nugroho','Ibu Siti Nugroho',NULL),
(2024000015,'73552eeb3ae4a9f520b6b349e50b66e602feae4e1302aa1d624a03b286aba661','Dewi Susilo','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081274378643','Jl. Pendidikan No. 15, Kota Pelajar','Konghucu','3201879257899465','3201510578526532','Ayah Dewi Susilo','Ibu Dewi Susilo',NULL),
(2024000016,'19a5197d62141d10c28605cc15630c802c50e257c2936ca85c25a43df2661f61','Lestari Saputra','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081287707850','Jl. Pendidikan No. 16, Kota Pelajar','Budha','3201138637934240','3201156379078375','Ayah Lestari Saputra','Ibu Lestari Saputra',NULL),
(2024000017,'bf4248f8856972750f0a71bf8203a67273259124736ed614bf4558f897090bc5','Eko Saputra','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081258124611','Jl. Pendidikan No. 17, Kota Pelajar','Katolik','3201526613571173','3201531909536869','Ayah Eko Saputra','Ibu Eko Saputra',NULL),
(2024000018,'752ee39fb797f9c5e6393e7eb634048174b639194203a3f2f800e3209cd296a6','Hendra Setiawan','laki-laki','Teknologi Informasi','Sistem Informasi','2024-08-01','081293665496','Jl. Pendidikan No. 18, Kota Pelajar','Islam','3201569710311365','3201280405370947','Ayah Hendra Setiawan','Ibu Hendra Setiawan',NULL),
(2024000019,'f5445a19de292c6b48babbcd644a06c695275a48ef528720a2aed01736538fa0','Rina Wijaya','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081253093531','Jl. Pendidikan No. 19, Kota Pelajar','Islam','3201414144231076','3201392942721533','Ayah Rina Wijaya','Ibu Rina Wijaya',NULL),
(2024000020,'75cf7f70e1b35c2e059a8d113794b060f8d3892234a9d0127ce9289d6feb3fbe','Sari Setiawan','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081239163256','Jl. Pendidikan No. 20, Kota Pelajar','Konghucu','3201826524875359','3201840823929347','Ayah Sari Setiawan','Ibu Sari Setiawan',NULL),
(2024000021,'90395c8fcc3efd73d7fc55ae76f4e36448dfe22e56c1de288a74cf0fc4705a85','Eko Utomo','laki-laki','Teknologi Informasi','Sistem Informasi','2024-08-01','081268336319','Jl. Pendidikan No. 21, Kota Pelajar','Budha','3201780517173555','3201904599102455','Ayah Eko Utomo','Ibu Eko Utomo',NULL),
(2024000022,'0aecc88479a5ed203797aee3a6afdf3b243adedb8851d601fa62f6ef49700156','Siti Hidayat','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081241289719','Jl. Pendidikan No. 22, Kota Pelajar','Kristen','3201465172372388','3201791280224919','Ayah Siti Hidayat','Ibu Siti Hidayat',NULL),
(2024000023,'bbf3a4e41adad0d1bda32aecc4f2c281a30a624cf0f96b6fb0245237a16e5c3d','Andi Wijaya','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081294583376','Jl. Pendidikan No. 23, Kota Pelajar','Islam','3201297616828922','3201166577314344','Ayah Andi Wijaya','Ibu Andi Wijaya',NULL),
(2024000024,'bc1c80d87c59fe2596ff9f7144d56e3e8b5ea4e4a92ffa8f0cdcf4708755591d','Indah Saputra','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081272625565','Jl. Pendidikan No. 24, Kota Pelajar','Konghucu','3201407460953233','3201819538981351','Ayah Indah Saputra','Ibu Indah Saputra',NULL),
(2024000025,'0f7ab59126d876b5a366bbc401cd2592f4d3b963e0523e9c3b05d3b12d47e6be','Indah Setiawan','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081241958560','Jl. Pendidikan No. 25, Kota Pelajar','Islam','3201634135557759','3201949830005006','Ayah Indah Setiawan','Ibu Indah Setiawan',NULL),
(2024000026,'deaebe94305fa6165bad7845f985b8493c38f7a186338ceb0b41bd9a9f6acd91','Wati Prasetyo','perempuan','Ekonomi','Akuntansi','2024-08-01','081253679675','Jl. Pendidikan No. 26, Kota Pelajar','Hindu','3201401997156383','3201204161409744','Ayah Wati Prasetyo','Ibu Wati Prasetyo',NULL),
(2024000027,'72f627922194e31993eb415e8e05cce15f38df362a014f532fe89e4aaaaf57fe','Putri Susilo','perempuan','Teknologi Informasi','Teknik Informatika','2024-08-01','081294616274','Jl. Pendidikan No. 27, Kota Pelajar','Kristen','3201800467961928','3201224299668969','Ayah Putri Susilo','Ibu Putri Susilo',NULL),
(2024000028,'d87dc876dcc297221a59e982e618f1dbe167d253bc09f8c6107e6e41ac23fe60','Ani Santoso','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081296402732','Jl. Pendidikan No. 28, Kota Pelajar','Islam','3201864424906114','3201848910960047','Ayah Ani Santoso','Ibu Ani Santoso',NULL),
(2024000029,'c3ae69e22c1a311ce0af2b7c1ad9d3d901fd6e78ea2de623b0eee596d1a5886f','Putri Santoso','perempuan','Ekonomi','Akuntansi','2024-08-01','081240492215','Jl. Pendidikan No. 29, Kota Pelajar','Hindu','3201788801326037','3201137679920359','Ayah Putri Santoso','Ibu Putri Santoso',NULL),
(2024000030,'51e78d8c7930838bd87d53a9770d2220bc2fabb7b9c13746f47fdfe14ec22460','Indah Saputra','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081234780321','Jl. Pendidikan No. 30, Kota Pelajar','Budha','3201610681547146','3201225882235819','Ayah Indah Saputra','Ibu Indah Saputra',NULL),
(2024000031,'91095998e66ecc23ec47bc1843123c7783c993cae225474435416de3a85d2602','Dedi Nugroho','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081297740260','Jl. Pendidikan No. 31, Kota Pelajar','Hindu','3201302871264672','3201371721206524','Ayah Dedi Nugroho','Ibu Dedi Nugroho',NULL),
(2024000032,'6fc9fcb3922d34378424427dd8cd899606422fce875e33fcc54a6bb0e365518d','Rudi Prasetyo','laki-laki','Teknologi Informasi','Sistem Informasi','2024-08-01','081299662515','Jl. Pendidikan No. 32, Kota Pelajar','Kristen','3201456293316025','3201343243697932','Ayah Rudi Prasetyo','Ibu Rudi Prasetyo',NULL),
(2024000033,'3954ada69553399cec9b83de25ee769306449f63eecc8279a303c921b3d603b0','Rudi Kurniawan','laki-laki','Ekonomi','Akuntansi','2024-08-01','081297982221','Jl. Pendidikan No. 33, Kota Pelajar','Hindu','3201715717268784','3201174464849276','Ayah Rudi Kurniawan','Ibu Rudi Kurniawan',NULL),
(2024000034,'0335fc9b36b305ad8a69991c76e33d5e9d180578ecd5ceee357cdbbf14130db5','Eko Setiawan','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081271198021','Jl. Pendidikan No. 34, Kota Pelajar','Hindu','3201203438763905','3201983155786735','Ayah Eko Setiawan','Ibu Eko Setiawan',NULL),
(2024000035,'4b498027197f68e719620580824420c95642f0848551220c185b37cf135b574f','Putri Saputra','perempuan','Ekonomi','Akuntansi','2024-08-01','081292721143','Jl. Pendidikan No. 35, Kota Pelajar','Konghucu','3201116160178116','3201255685837859','Ayah Putri Saputra','Ibu Putri Saputra',NULL),
(2024000036,'679b3be347d8167d3979c895f6cbdf39defdc41d948c3a384e889aff6729f088','Indah Nugroho','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081220401518','Jl. Pendidikan No. 36, Kota Pelajar','Kristen','3201638751218161','3201340489658826','Ayah Indah Nugroho','Ibu Indah Nugroho',NULL),
(2024000037,'78c6347b92cac501a2ae1282d53c38263c0f29beb885e9dc270c03d0c852c718','Sari Utomo','perempuan','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081212254601','Jl. Pendidikan No. 37, Kota Pelajar','Islam','3201303789390917','3201428472596197','Ayah Sari Utomo','Ibu Sari Utomo',NULL),
(2024000038,'496c688af1c77921744998f5ce27ce23570d84d9a297f41deca76a59a4eb3296','Indah Susilo','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081224383070','Jl. Pendidikan No. 38, Kota Pelajar','Kristen','3201579597456936','3201486990701611','Ayah Indah Susilo','Ibu Indah Susilo',NULL),
(2024000039,'0972d9e61c2b5c26492891171e105a5d0e1c8c9ff5e587f8e150960cc4ca2eae','Hendra Setiawan','laki-laki','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081226094121','Jl. Pendidikan No. 39, Kota Pelajar','Konghucu','3201948690316742','3201947227183301','Ayah Hendra Setiawan','Ibu Hendra Setiawan',NULL),
(2024000040,'1eebf9e55cc2e9e4592ae4e506af3192cb72927dce4c6b6f843df9ebd2cc353c','Joko Prasetyo','laki-laki','Ekonomi','Akuntansi','2024-08-01','081217414556','Jl. Pendidikan No. 40, Kota Pelajar','Hindu','3201481331120488','3201997607041719','Ayah Joko Prasetyo','Ibu Joko Prasetyo',NULL),
(2024000041,'dc2b711083b8f164ecb04075197405188755be26cd50c1730dc16becf308d986','Eko Nugroho','laki-laki','Teknologi Informasi','Teknik Informatika','2024-08-01','081249329563','Jl. Pendidikan No. 41, Kota Pelajar','Hindu','3201556140112072','3201465475544581','Ayah Eko Nugroho','Ibu Eko Nugroho',NULL),
(2024000042,'a545da37acd2aec4578d886adcf4b3fc08b47c9032a051279035adf06240c34e','Eko Prasetyo','laki-laki','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081210298353','Jl. Pendidikan No. 42, Kota Pelajar','Kristen','3201381469855149','3201842356235834','Ayah Eko Prasetyo','Ibu Eko Prasetyo',NULL),
(2024000043,'eedd7e1fbae80a14c0015c411bde08624da5565e387932d5beb7d4b1ac783f4a','Rina Kurniawan','perempuan','Ekonomi','Akuntansi','2024-08-01','081276716066','Jl. Pendidikan No. 43, Kota Pelajar','Kristen','3201324404054678','3201511207781359','Ayah Rina Kurniawan','Ibu Rina Kurniawan',NULL),
(2024000044,'befdd7e22367a717854daf77daa7f168af57b87a4870c9e7cef083b5f5f86715','Siti Susilo','perempuan','Ekonomi','Akuntansi','2024-08-01','081287861728','Jl. Pendidikan No. 44, Kota Pelajar','Kristen','3201130876526625','3201449164225729','Ayah Siti Susilo','Ibu Siti Susilo',NULL),
(2024000045,'a134d4cb545d26f60630b1010330b2186df11299ad24df1ad615afc2462bc3b7','Joko Santoso','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081299451450','Jl. Pendidikan No. 45, Kota Pelajar','Hindu','3201771696844112','3201797028876800','Ayah Joko Santoso','Ibu Joko Santoso',NULL),
(2024000046,'865ae7f366e8ee7500743cfa44baadabc3012e66daab91eb7cd9492c7554d436','Rina Susilo','perempuan','Teknologi Informasi','Teknik Informatika','2024-08-01','081255483678','Jl. Pendidikan No. 46, Kota Pelajar','Budha','3201618098244400','3201941342950521','Ayah Rina Susilo','Ibu Rina Susilo',NULL),
(2024000047,'def11324d7374e27a222cd29cb016e1b66a12db18932276defce3d956c907f53','Agus Prasetyo','laki-laki','Teknologi Informasi','Sistem Informasi','2024-08-01','081269514579','Jl. Pendidikan No. 47, Kota Pelajar','Islam','3201380023943780','3201723465100310','Ayah Agus Prasetyo','Ibu Agus Prasetyo',NULL),
(2024000048,'fe1fa1fcc8d18f2d38ea0efcd8ff644521e9d2fcbab100397dd3e7666cedc7d8','Rina Utomo','perempuan','Teknologi Informasi','Sistem Informasi','2024-08-01','081217843973','Jl. Pendidikan No. 48, Kota Pelajar','Hindu','3201226678886924','3201700873278079','Ayah Rina Utomo','Ibu Rina Utomo',NULL),
(2024000049,'aa5606aed8f666bdf1889f9ea0816ad4bd3e83b0dbba14eb492f0e10316f2597','Dedi Utomo','laki-laki','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081215590209','Jl. Pendidikan No. 49, Kota Pelajar','Hindu','3201680927660434','3201735426773559','Ayah Dedi Utomo','Ibu Dedi Utomo',NULL),
(2024000050,'78eb632055e54e6481d8e8c60a56eaadd3ac4c8b54470db59018cf8c5fb55867','Andi Setiawan','laki-laki','Teknik Elektro','Teknik Telekomunikasi','2024-08-01','081261174497','Jl. Pendidikan No. 50, Kota Pelajar','Islam','3201651228150799','3201155141935324','Ayah Andi Setiawan','Ibu Andi Setiawan',NULL),
(2024000051,'d37242a1860be2763f38d2e7d1a257571d8ad81464394f47be68fd4117441185','Andi Saputra','laki-laki','Ekonomi','Akuntansi','2024-08-01','081241861596','Jl. Pendidikan No. 51, Kota Pelajar','Islam','3201259076631560','3201613373628712','Ayah Andi Saputra','Ibu Andi Saputra',NULL),
(2024000052,'f3b9982483929c209ebfb8d1fbfc8f0db22499bed9bdbde0f4209cb2e832ed98','Maya Utomo','perempuan','Ekonomi','Akuntansi','2024-08-01','081238928452','Jl. Pendidikan No. 52, Kota Pelajar','Kristen','3201359822566911','3201944933420037','Ayah Maya Utomo','Ibu Maya Utomo',NULL),
(2024000053,'d992fe6208f0c33abc13a70c1dc4aa18f1df6fd28f3cfe2f0d77b732fa540eef','Indah Santoso','perempuan','Ekonomi','Akuntansi','2024-08-01','081259414094','Jl. Pendidikan No. 53, Kota Pelajar','Islam','3201981612426724','3201235989471336','Ayah Indah Santoso','Ibu Indah Santoso',NULL),
(2024000054,'bea00d3718f0fd0fe4c31849dccf0114ce8fe96d5a9fdc5b583604429fc41b9e','Agus Santoso','laki-laki','Ekonomi','Akuntansi','2024-08-01','081283701392','Jl. Pendidikan No. 54, Kota Pelajar','Budha','3201227363978304','3201180176771859','Ayah Agus Santoso','Ibu Agus Santoso',NULL),
(2024000055,'e2b816b53e7aa3edc1ce3dbfbdfd3d3f083660a5be7f7d429f717153da30c5be','Bambang Prasetyo','laki-laki','Ekonomi','Akuntansi','2024-08-01','081267771808','Jl. Pendidikan No. 55, Kota Pelajar','Islam','3201995069961636','3201351284211326','Ayah Bambang Prasetyo','Ibu Bambang Prasetyo',NULL),
(2024000056,'29be710fa6bfb68365935e3b55a10ffed2d9f455f7c7f11bf14aa382fb89e17b','Sari Wijaya','perempuan','Teknik Mesin','Teknik Otomotif','2024-08-01','081274383446','Jl. Pendidikan No. 56, Kota Pelajar','Islam','3201718240905137','3201302499584398','Ayah Sari Wijaya','Ibu Sari Wijaya',NULL),
(2024000057,'952588e93c1e11edae2d88a215098fb7ae7813936477bacf906a871543d4aca1','Iwan Prasetyo','laki-laki','Teknik Mesin','Teknik Otomotif','2024-08-01','081269930083','Jl. Pendidikan No. 57, Kota Pelajar','Konghucu','3201840711602363','3201979491141350','Ayah Iwan Prasetyo','Ibu Iwan Prasetyo',NULL),
(2024000058,'962e61535af70b9c3759cf55858b894a27a87b470f9e343aecafc9b78d1dbbd2','Hendra Santoso','laki-laki','Teknologi Informasi','Sistem Informasi','2024-08-01','081218113975','Jl. Pendidikan No. 58, Kota Pelajar','Budha','3201692461690876','3201716728644872','Ayah Hendra Santoso','Ibu Hendra Santoso',NULL),
(2024000059,'afce829d7ce6d66f7cb4a949aad67e7dbe986b150eda9018e96f6a6996d8d908','Eko Santoso','laki-laki','Teknologi Informasi','Teknik Informatika','2024-08-01','081238660837','Jl. Pendidikan No. 59, Kota Pelajar','Konghucu','3201657046630398','3201130219713402','Ayah Eko Santoso','Ibu Eko Santoso',NULL),
(2024000060,'7279d32b3e99898397b88dd0426a21e0bd7adcb19b03345a5d133d99c4282086','Wati Prasetyo','perempuan','Ekonomi','Akuntansi','2024-08-01','081289527136','Jl. Pendidikan No. 60, Kota Pelajar','Konghucu','3201736397657341','3201416718086291','Ayah Wati Prasetyo','Ibu Wati Prasetyo',NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD PRIMARY KEY (`nim`),
  ADD KEY `nama_on_mahasiswa` (`nama`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

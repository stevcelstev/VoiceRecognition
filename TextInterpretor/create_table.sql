USE [tiln]
GO

/****** Object:  Table [dbo].[gps_data]    Script Date: 5/3/2020 5:20:17 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[gps_data](
	[id] [numeric](18, 0) NULL,
	[ora] [char](10) NULL,
	[data] [char](20) NULL,
	[adresa] [nchar](100) NULL
) ON [PRIMARY]
GO
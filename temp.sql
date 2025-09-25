
-- =============================================
-- Author:		<Author,,Name>
-- Create date: <2025.8.11>
-- Description:	股权回购汇总表
--  [SYS_P_shareholderTotal]  '%'
-- =============================================
create  PROCEDURE [dbo].[SYS_P_shareholderTotal]
	@dptName varchar(30)  --单位
AS

declare   @tmp table(
	dptName varchar(10),  --单位
	manQty	int,		  --股东数
	shareholderQty dec,   --股权总
	signQty	int,          --签约人数
	saleQty int           --签约股数
)

insert into @tmp(dptName,manQty,shareholderQty)	
select dptName,COUNT(*) as manQty,SUM(qtyTotal) as shareholderQty 
from table_holder_info
where dptName like @dptName
group by dptName

update @tmp set signQty = B.signQty,saleQty = B.saleQty
from (
	select B.dptName,
	   SUM(case remark when '已签约' then 1 else 0 end) as SignQty,     --统计已签约人数
	   SUM(case remark when '已签约' then saleQty else 0 end) as saleQty  --汇总已签约股数
	from table_record A inner join table_holder_info B on A.shareholderId = B.shareholderId
	group by B.dptName
) B inner join @tmp A on  A.dptName = B.dptName

select dptName,manQty,signQty,shareholderQty,saleQty
 from @tmp order by A.dptName

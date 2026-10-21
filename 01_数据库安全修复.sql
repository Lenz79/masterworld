-- 星轨智盘 bazi_records 专用迁移；请先备份并阅读说明。
-- 只修改 public.bazi_records；不删除任何历史数据。
BEGIN;

ALTER TABLE public.bazi_records
  ADD COLUMN IF NOT EXISTS user_id uuid;

CREATE INDEX IF NOT EXISTS bazi_records_user_id_created_at_idx
  ON public.bazi_records (user_id, created_at DESC);

ALTER TABLE public.bazi_records ENABLE ROW LEVEL SECURITY;

-- 撤销已证实的公开 ALL + true/true 政策。
DROP POLICY IF EXISTS "Allow public access" ON public.bazi_records;

-- 避免重复执行时产生重名政策。
DROP POLICY IF EXISTS "xinggui_owner_select" ON public.bazi_records;
DROP POLICY IF EXISTS "xinggui_owner_insert" ON public.bazi_records;
DROP POLICY IF EXISTS "xinggui_owner_update" ON public.bazi_records;
DROP POLICY IF EXISTS "xinggui_owner_delete" ON public.bazi_records;

CREATE POLICY "xinggui_owner_select" ON public.bazi_records
  FOR SELECT TO authenticated USING ((select auth.uid()) = user_id);
CREATE POLICY "xinggui_owner_insert" ON public.bazi_records
  FOR INSERT TO authenticated WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY "xinggui_owner_update" ON public.bazi_records
  FOR UPDATE TO authenticated
  USING ((select auth.uid()) = user_id)
  WITH CHECK ((select auth.uid()) = user_id);
CREATE POLICY "xinggui_owner_delete" ON public.bazi_records
  FOR DELETE TO authenticated USING ((select auth.uid()) = user_id);

-- 防止旧的 PUBLIC/anon 授权与开放政策组合形成访问入口。
REVOKE ALL ON TABLE public.bazi_records FROM PUBLIC, anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.bazi_records TO authenticated;

COMMIT;

-- 只读验收：现有旧记录应保留；旧记录 user_id 为空，暂不自动归属任何账号。
SELECT COUNT(*) AS total_records,
       COUNT(*) FILTER (WHERE user_id IS NULL) AS unassigned_records
FROM public.bazi_records;
SELECT policyname, roles, cmd, qual, with_check
FROM pg_policies WHERE schemaname='public' AND tablename='bazi_records'
ORDER BY policyname;

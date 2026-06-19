-- Run only when the old MVP schema exists and before applying Alembic 0001.
-- This preserves previous data while freeing the final table names.

ALTER TABLE IF EXISTS public.usuarios RENAME TO legacy_usuarios;
ALTER TABLE IF EXISTS public.ejercicios RENAME TO legacy_ejercicios;
ALTER TABLE IF EXISTS public.sesiones RENAME TO legacy_sesiones;
ALTER TABLE IF EXISTS public.conversaciones RENAME TO legacy_conversaciones;
ALTER TABLE IF EXISTS public.mensajes RENAME TO legacy_mensajes;

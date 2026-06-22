Queries


**¿Cómo se ve en la base que el usuario terminó un juego?**

```sql
SELECT s.fin_en, c.juego_id
FROM sesiones s
JOIN conversaciones c ON c.sesion_id = s.id
WHERE s.estudiante_id = '<uuid>'
  AND s.estado = 'cerrada'
ORDER BY c.juego_id, s.fin_en;

```
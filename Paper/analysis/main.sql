-- Turns → 13.5 ± 13.5
SELECT ROUND(AVG(turnos), 1) AS media,
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Messages → 27.9 ± 27.1
SELECT ROUND(AVG(mensajes), 1) AS media,
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Questions → 2.2 ± 2.7
SELECT ROUND(AVG(preguntas), 1) AS media,
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Duration (min) → 13.8 ± 13.9
SELECT ROUND(AVG(duracion_min), 1) AS media,
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

-- Blocks sugg. → 6.8 ± 7.6
SELECT ROUND(AVG(bloques_sugeridos), 1) AS media,
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*) - 1.0)), 1) AS sd
FROM v_ms_pub;

SELECT 1 AS ord, 'Turns' AS celda,
       ROUND(AVG(turnos),1) || ' ± ' ||
       ROUND(SQRT((SUM(turnos*turnos) - COUNT(*)*AVG(turnos)*AVG(turnos))
                  / (COUNT(*)-1.0)),1) AS valor, COUNT(*) AS n
FROM v_ms_pub
UNION ALL SELECT 2, 'Messages',
       ROUND(AVG(mensajes),1) || ' ± ' ||
       ROUND(SQRT((SUM(mensajes*mensajes) - COUNT(*)*AVG(mensajes)*AVG(mensajes))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 3, 'Questions',
       ROUND(AVG(preguntas),1) || ' ± ' ||
       ROUND(SQRT((SUM(preguntas*preguntas) - COUNT(*)*AVG(preguntas)*AVG(preguntas))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 4, 'Duration (min)',
       ROUND(AVG(duracion_min),1) || ' ± ' ||
       ROUND(SQRT((SUM(duracion_min*duracion_min)
                   - COUNT(*)*AVG(duracion_min)*AVG(duracion_min))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
UNION ALL SELECT 5, 'Blocks sugg.',
       ROUND(AVG(bloques_sugeridos),1) || ' ± ' ||
       ROUND(SQRT((SUM(bloques_sugeridos*bloques_sugeridos)
                   - COUNT(*)*AVG(bloques_sugeridos)*AVG(bloques_sugeridos))
                  / (COUNT(*)-1.0)),1), COUNT(*) FROM v_ms_pub
ORDER BY ord;

/*
 ord   celda            valor          n
   1   Turns            13.5 ± 13.5    98
   2   Messages         27.9 ± 27.1    98
   3   Questions        2.2 ± 2.7      98
   4   Duration (min)   13.8 ± 13.9    98
   5   Blocks sugg.     6.8 ± 7.6      98
-------------------------------------------
│ ord │     celda      │    valor    │ n  │
╞═════╪════════════════╪═════════════╪════╡
│   1 │ Turns          │ 13.5 ± 13.5 │ 98 │
│   2 │ Messages       │ 27.9 ± 27.1 │ 98 │
│   3 │ Questions      │ 2.2 ± 2.7   │ 98 │
│   4 │ Duration (min) │ 13.8 ± 13.9 │ 98 │
│   5 │ Blocks sugg.   │ 6.8 ± 7.6   │ 98 │
-------------------------------------------
*/

SELECT *
FROM performance_summary;

SELECT *
FROM performance_summary
ORDER BY "Sharpe Ratio" DESC;

SELECT
    Column1 AS Theme,
    "Annualized Return",
    "Annualized Volatility",
    "Sharpe Ratio"
FROM performance_summary
WHERE "Sharpe Ratio" > 1.0
ORDER BY "Sharpe Ratio" DESC;

SELECT
    AVG(AI) AS avg_ai_return,
    AVG(Energy) AS avg_energy_return,
    AVG(Biotech) AS avg_biotech_return,
    AVG(Space) AS avg_space_return,
    AVG(VOO) AS avg_voo_return
FROM annual_returns;

SELECT
    AVG(AI) AS avg_ai_return,
    AVG(Energy) AS avg_energy_return,
    AVG(Biotech) AS avg_biotech_return,
    AVG(Space) AS avg_space_return,
    AVG(VOO) AS avg_voo_return
FROM annual_returns
WHERE Year < 2026;

SELECT
    Column1 AS Theme,
    VOO AS Correlation_With_VOO
FROM correlation_matrix
WHERE Column1 <> 'VOO'
ORDER BY VOO ASC;

SELECT
    Year,
    AI,
    Energy,
    Biotech,
    Space,
    VOO
FROM annual_returns
ORDER BY Year;
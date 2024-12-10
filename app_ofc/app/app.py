import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db
import urllib.parse

APP = Flask(__name__)


@APP.route('/Paciente/')
def index5():
    #tabela de pacientes 
    stats = db.execute('''
       SELECT * 
       from Paciente
    ''').fetchall()
    return render_template('Paciente.html',paciente=stats)

@APP.route('/Periodo/')
def periodo():
    #tabela de periodo
    stats = db.execute('''
       SELECT * 
       from Periodo
    ''').fetchall()
    return render_template('Periodo.html',periodo=stats)

@APP.route('/Regiao/')
def index1():
    #tabela de regiao
    stats = db.execute('''
       SELECT * 
       from Regiao
    ''').fetchall()
    return render_template('Regiao.html',regiao=stats)

@APP.route('/Diagnostico/')
def index2():
    #tabela de diagnostico 
    stats = db.execute('''
       SELECT * 
       from diagnostico
    ''').fetchall()
    return render_template('Diagnostico.html',diagnostico=stats)

@APP.route('/Instituicao/')
def index3():
    #tabela de Instituicao 
    stats = db.execute('''
        SELECT * 
        FROM Instituicao
        ORDER BY nome
    ''').fetchall()
    return render_template('ListarInstituicao.html',instituicao=stats)

@APP.route('/Clinic_Stats/')
def index4():
    #tabela de clinic 
    stats = db.execute('''
       SELECT * 
       from ClinicStats
    ''').fetchall()
    return render_template('Clinic_Stats.html',clinic=stats)

    
# Start page
@APP.route('/')
def index():
    #primeira queria que vai para o display inicial
    stats = db.execute('''
       SELECT * FROM
            (SELECT COUNT(*) as n_period FROM Periodo)
        JOIN
            (SELECT COUNT(*) as n_inter FROM ClinicStats)
        JOIN
            (SELECT COUNT(*) as n_pac FROM Paciente)
        JOIN
            (SELECT COUNT(*) as n_diag FROM Diagnostico)
        JOIN
            (SELECT COUNT(*) as n_inst FROM Instituicao)
        JOIN
            (SELECT COUNT(*) as n_reg FROM Regiao)
    ''').fetchone()
    return render_template('index.html',stats=stats)

@APP.route('/DiagnosticosPorHospital/')
def one():
    stuff = db.execute('''
    SELECT 
        i.nome AS Hospital,
        d.nome AS Diagnostico,
        COUNT(DISTINCT d.id) AS Num_DiagDif,
        SUM(c.internamentos) AS Total_Internamentos,
        MAX(c.diasInternamento) AS Max_Dias_Internamento,
        SUM(c.ambulatorio) AS Total_Ambulatorio,
        SUM(c.obitos) AS Total_Obitos
    FROM 
        ClinicStats c
    JOIN 
        Diagnostico d ON c.id = d.id
    JOIN 
        Instituicao i ON c.instituicao = i.nome
    GROUP BY 
        i.nome, d.nome
    ORDER BY 
        i.nome ASC, d.nome ASC
    ''').fetchall()
    return render_template('Diag_Hosp.html', stuff=stuff)


@APP.route('/Instituicao/<string:nome>/')
def instituicao(nome):
    # Obtém clinicstats por hospital
    nome = urllib.parse.unquote(nome)
    instituicao = db.execute('''
    SELECT 
        d.nome AS Diagnostico,
        SUM(c.internamentos) AS Total_Internamentos,
        MAX(c.diasInternamento) AS Max_Dias_Internamento,
        SUM(c.ambulatorio) AS Total_Ambulatorio,
        SUM(c.obitos) AS Total_Obitos
    FROM 
        ClinicStats c
    JOIN 
        Diagnostico d ON c.id = d.id
    JOIN 
        Instituicao i ON c.instituicao = i.nome
    WHERE 
        i.nome like ?
    GROUP BY 
        i.nome, d.nome
    ORDER BY 
        d.nome ASC
    ''', [nome]).fetchall()

    regiao =  db.execute('''
    SELECT regiao
    FROM Instituicao
    WHERE Instituicao.nome like ?
    ''', [nome]).fetchone()
    return render_template('Instituicao.html', instituicao=instituicao, nome=nome, regiao=regiao)


@APP.route('/regiao_d/')
def r_diagnostico():
    # Quais regiões possuem mais óbitos, internaçoes e ambulatórios
    r_diagnostico = db.execute('''
        SELECT r.nome, sum(c.obitos) AS Obitos, sum(c.internamentos) AS Internamentos, sum(c.ambulatorio) AS Ambulatório, sum(c.diasInternamento) AS diasInternamento 
        FROM Regiao r
        JOIN Instituicao i ON r.nome = i.regiao
        JOIN ClinicStats c ON i.nome = c.instituicao
        GROUP BY r.nome
        ORDER BY Obitos DESC, Internamentos, Ambulatório, diasInternamento
    ''').fetchall()
    return render_template('regiao_d.html',
                            diagnostico=r_diagnostico)



@APP.route('/Pacientes_Internacao/')
def p_interna():
    # Pacientes com diagnosticos que resultaram em maior numero de internações por faixa etaria 
    p_internacoes = db.execute('''
        SELECT d.nome AS Diagnostico, p.genero AS Genero, MAX(c.internamentos) AS Numero_Internamentos, p.faixaEtaria AS Faixa_Etaria
        FROM ClinicStats c
        JOIN Paciente p ON c.IDP = p.IDP
        JOIN Diagnostico d ON c.ID = d.ID
        GROUP BY d.nome, p.faixaEtaria 
        ORDER BY Faixa_Etaria ASC
    ''').fetchall()
    return render_template('p_internacoes.html',
                           Pacientes=p_internacoes)

@APP.route('/Diagnostico_Hospital/')
def d_hospital():
    # Todos os diagnosticos sem internamentos em cada hospital
    d_hospital = db.execute('''
        SELECT i.nome AS Hospital, d.nome AS Diagnostico, c.internamentos AS Internamentos
        FROM Instituicao i
        CROSS JOIN Diagnostico d
        LEFT JOIN ClinicStats c ON i.nome = c.ID AND d.ID = c.ID
        GROUP BY i.nome, d.nome
        HAViNG COUNT(c.internamentos) = 0
        ORDER BY i.nome, d.nome
    ''').fetchall()
    return render_template('Diag_Hosp.html',
                                Diagnostico=d_hospital)

@APP.route('/Ambulatorios_Q/')
def ambulatorios_quanti():
    # Numero de ambulatorios em relação ao diagnostico
    ambulatorios_quanti = db.execute('''
        SELECT d.nome AS Diagnostico, p.faixaEtaria AS Faixa_Etaria, COUNT(c.ambulatorio) AS Ambulatorios, SUM(c.internamentos) AS Internamentos,
        (COUNT(c.ambulatorio) / SUM(c.internamentos)) AS AmbulatorioInternacao
        FROM ClinicStats c
        JOIN Diagnostico d ON c.id = d.id
        JOIN Paciente p ON c.idp = p.idp
        GROUP BY d.nome, p.faixaEtaria
        ORDER BY Faixa_Etaria, Ambulatorios, Internamentos DESC;
    ''').fetchall()
    return render_template('ambulatorios_quanti.html',
                                Ambulatorios=ambulatorios_quanti)

@APP.route('/listar/')
def oneQuery():
    clinicstats = db.execute('''
    SELECT 
        i.nome AS Hospital,
        d.nome AS Diagnostico,
        SUM(c.internamentos) AS Total_Internamentos,
        MAX(c.diasInternamento) AS Max_Dias_Internamento,
        SUM(c.ambulatorio) AS Total_Ambulatorio,
        SUM(c.obitos) AS Total_Obitos
    FROM 
        ClinicStats c
    JOIN 
        Diagnostico d ON c.id = d.id
    JOIN 
        Instituicao i ON c.instituicao = i.nome
    GROUP BY 
        i.nome, d.nome
    ORDER BY 
        i.nome ASC, d.nome ASC
    ''').fetchall()
    return render_template("listar.html", clinicstats=clinicstats)

@APP.route('/Diag_Pac/')
def diagpac():
    stats = db.execute('''
        WITH RankedInternamentos AS (
        SELECT p.IDP AS Paciente,
        d.nome AS Diagnostico,
        p.faixaEtaria AS Faixa_Etaria,
        c.internamentos AS Internamentos,
        ROW_NUMBER() OVER (PARTITION BY d.nome ORDER BY c.internamentos DESC) AS Rank
        FROM ClinicStats c
        JOIN Paciente p ON c.IDP = p.IDP
        JOIN Diagnostico d ON c.ID = d.ID
        WHERE c.internamentos > (
        SELECT AVG(internamentos)
        FROM ClinicStats
        )
        )
        SELECT Paciente, Diagnostico, Faixa_Etaria, Internamentos
        FROM RankedInternamentos
        WHERE Rank = 1
        ORDER BY Faixa_Etaria ASC, Diagnostico ASC;
    ''').fetchall()
    return render_template("Diag_Pac.html", stats=stats)



@APP.route('/nadafeito/')
def naday():
    nada = db.execute('''
SELECT c.Instituicao AS Instituicao_ID,
c.ID AS Diagnostico_ID,
d.nome AS Diagnostico_Nome
FROM ClinicStats c
JOIN Diagnostico d ON c.ID = d.ID
GROUP BY c.ID, d.nome, c.Instituicao
HAVING SUM(c.internamentos) = 0
ORDER BY Instituicao_ID;
    ''').fetchall()
    return render_template("nadafeito.html", nada=nada)

@APP.route('/pergunta9/')
def rankedObitos():
    # Numero de ambulatorios em relação ao diagnostico
    stats = db.execute('''
        WITH ProporcaoObitos AS (
    SELECT r.nome AS Regiao,
           SUM(c.obitos) AS Total_Obitos,
           SUM(c.internamentos) AS Total_Internamentos,
           CAST(SUM(c.obitos) AS FLOAT) / NULLIF(SUM(c.internamentos), 0) AS Proporcao
    FROM ClinicStats c join instituicao i on c.instituicao=i.nome
    JOIN Regiao r on i.regiao=r.nome
    GROUP BY r.nome
),
MediaGlobal AS (
    SELECT AVG(Proporcao) AS Media_Proporcao_Global
    FROM ProporcaoObitos
)
SELECT p.Regiao,
       p.Total_Obitos,
       p.Total_Internamentos,
       p.Proporcao,
       m.Media_Proporcao_Global
FROM ProporcaoObitos p
CROSS JOIN MediaGlobal m
ORDER BY p.Proporcao DESC;
    ''').fetchall()
    return render_template('pergunta9.html',
                                stats=stats)

#Pergunta 8
@APP.route('/pergunta8/')
def obitosInst():
    # Periodo com o maior Nº de Óbitos por Instituição 
    stats = db.execute('''
WITH t AS (
    SELECT 
        i.nome AS Hospital,
        c.data AS Data,
        SUM(c.obitos) AS Total_Obitos
    FROM 
        ClinicStats c
    JOIN 
        Instituicao i ON c.instituicao = i.nome
    GROUP BY 
        i.nome, c.data
),
ranked AS (
    SELECT 
        t.Hospital, 
        t.Data, 
        t.Total_Obitos,
        ROW_NUMBER() OVER (PARTITION BY t.Hospital ORDER BY t.Total_Obitos DESC) AS rn
    FROM 
        t
)
SELECT 
    Hospital, 
    Data, 
    Total_Obitos
FROM 
    ranked
WHERE 
    rn = 1; ''').fetchall()
    return render_template('pergunta8.html',stats=stats)

@APP.route('/hpor/')
def hpor():
    stats= db.execute('''
SELECT regiao, COUNT(nome) AS n_hospitais
FROM Instituicao
group by regiao
    ''').fetchall() 
    return render_template("hpor.html", hpor=stats)

@APP.route('/or/')
def eor():
    stats= db.execute('''
SELECT 
    p.faixaEtaria,
    d.nome AS diagnostico,
    i.nome AS instituicao,
    COUNT(DISTINCT c.IDP) AS total_ambulatorios,  
    SUM(CASE WHEN c.internamentos > 0 THEN 1 ELSE 0 END) AS total_internamentos  
FROM ClinicStats c
JOIN Paciente p ON c.IDP = p.IDP
JOIN Diagnostico d ON c.ID = d.ID
JOIN Instituicao i ON c.instituicao = i.nome
GROUP BY p.faixaEtaria, d.nome, i.nome
HAVING COUNT(DISTINCT c.IDP) > SUM(CASE WHEN c.internamentos > 0 THEN 1 ELSE 0 END);
    ''').fetchall() 
    return render_template("or.html", eor=stats)

@APP.route('/pergunta11/')
def pergunta11():
    # Encontre a média, mediana e desvio padrão do número de dias de internamento por faixa etária.
    stats = db.execute('''
WITH Media AS (
    SELECT ClinicStats.diasinternamento, Paciente.faixaEtaria 
    FROM ClinicStats 
    INNER JOIN  Paciente 
    ON ClinicStats.IDP = Paciente.IDP
), 
Mediana AS (
    SELECT faixaEtaria, diasinternamento,
        ROW_NUMBER() OVER (PARTITION BY faixaEtaria ORDER BY diasinternamento) AS rn,
        COUNT(*) OVER (PARTITION BY faixaEtaria) AS total
    FROM  Media
), 
DesvioPadrao AS (
    SELECT faixaEtaria,AVG(diasinternamento) AS media,
        SUM(diasinternamento * diasinternamento) AS soma_quadrados,
        COUNT(*) AS total_registros
    FROM Media
    GROUP BY faixaEtaria
)
SELECT o.faixaEtaria,m.media,
    MAX(CASE WHEN o.rn = (o.total + 1) / 2 THEN o.diasinternamento END) AS mediana,
    SQRT(SUM(POWER(o.diasinternamento - m.media, 2)) / m.total_registros) AS desvioPadrao
FROM Mediana o
JOIN DesvioPadrao m
ON o.faixaEtaria = m.faixaEtaria
GROUP BY o.faixaEtaria, m.media, m.total_registros
; ''').fetchall()
    return render_template('pergunta11.html',pergunta=stats)

@APP.route('/pergunta13/')
def pergunta13(): 
    stats = db.execute('''
SELECT d.nome as Diagnóstico, p.faixaEtaria as "Faixa_Etária", count(*) as Ocorrências
FROM ClinicStats c join Diagnostico d join Paciente p on d.ID = c.ID and c.IDP = p.IDP
group by d.nome, p.faixaEtaria;
 ''').fetchall()
    return render_template('pergunta13.html',pergunta13=stats)

@APP.route('/pergunta5/')
def pergunta5(): 
    stats = db.execute('''
SELECT d.nome as Diagnóstico,
sum(c.internamentos) as Internamentos,
sum(c.diasInternamento) as "Dias_de_Internamento",
(sum(c.diasInternamento)/sum(c.internamentos)) as "Tempo_médio_de_internamento"
FROM Diagnostico d
NATURAL JOIN ClinicStats c
group by d.nome
    ''').fetchall()
    return render_template('pergunta5.html',pergunta5=stats)

@APP.route('/pergunta10/')
def pergunta10(): 
    stats = db.execute('''

WITH ProporcaoObitos AS (
SELECT r.nome AS Regiao,
SUM(c.obitos) AS Total_Obitos,
SUM(c.internamentos) AS Total_Internamentos,
CAST(SUM(c.obitos) AS FLOAT) / NULLIF(SUM(c.internamentos), 0) AS Proporcao
FROM ClinicStats c join instituicao i on c.instituicao=i.nome
JOIN Regiao r on i.regiao=r.nome
GROUP BY r.nome
),
MediaGlobal AS (
SELECT AVG(Proporcao) AS Media_Proporcao_Global
FROM ProporcaoObitos
)
SELECT p.Regiao,
p.Total_Obitos,
p.Total_Internamentos,
p.Proporcao,
m.Media_Proporcao_Global
FROM ProporcaoObitos p
CROSS JOIN MediaGlobal m
ORDER BY p.Proporcao DESC;
    ''').fetchall()
    return render_template('pergunta10.html',pergunta10=stats)

@APP.route('/pergunta3/')
def pergunta3():
    # Óbitos em comparação ao ano, por instituição e diagnóstico:
    stats = db.execute('''
SELECT
    c.data As Período, 
    c.instituicao AS Hospital, 
    d.nome AS Diagnóstico, 
    SUM(c.obitos) AS Óbitos
FROM 
    ClinicStats c
JOIN 
    Diagnostico d 
ON 
    d.ID = c.ID
GROUP BY 
    d.nome, c.data, c.instituicao
ORDER BY 
    c.instituicao, d.nome, c.data
; ''').fetchall()
    return render_template('pergunta3.html',pergunta=stats)

@APP.route('/pergunta12/')
def pergunta12(): 
    stats = db.execute('''
SELECT c.data AS Data, 
i.regiao AS Regiao, 
AVG(c.internamentos) as Internamentos
FROM ClinicStats c
JOIN Instituicao i ON i.nome = c.instituicao
GROUP BY c.data, i.regiao
ORDER BY c.data, c.internamentos
; ''').fetchall()
    return render_template('pergunta12.html',pergunta12=stats)

@APP.route('/pergunta14/')
def pergunta14(): 
    stats = db.execute('''
select Diagnóstico, Faixa_Etaria, max(Ocorrências) as Quantidade
from
(SELECT d.nome as Diagnóstico, p.faixaEtaria as Faixa_Etaria, count(*) as Ocorrências
FROM ClinicStats c join Diagnostico d join Paciente p on d.ID = c.ID and c.IDP = p.IDP
group by d.nome, p.faixaEtaria)
group by Diagnóstico
order by Quantidade;
 ''').fetchall()
    return render_template('pergunta14.html',pergunta14=stats)


@APP.route('/pergunta15/')
def pergunta15(): 
    stats = db.execute('''
SELECT 
        i.nome AS Hospital,
        d.nome AS Diagnostico,
        SUM(c.internamentos) AS Total_Internamentos,
        MAX(c.diasInternamento) AS Max_Dias_Internamento,
        SUM(c.ambulatorio) AS Total_Ambulatorio,
        SUM(c.obitos) AS Total_Obitos
    FROM ClinicStats c
    JOIN Diagnostico d ON c.id = d.id
    JOIN Instituicao i ON c.instituicao = i.nome
    GROUP BY i.nome, d.nome
    ORDER BY  i.nome ASC, d.nome ASC


 ''').fetchall()
    return render_template('pergunta15.html',pergunta15=stats)

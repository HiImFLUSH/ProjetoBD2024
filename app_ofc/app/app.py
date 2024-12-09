import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

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

@APP.route('/ClinicStats/')
def listar_clinicstats():
    #que pregunta é esta ??????????
    clinicstats = db.execute('''
    SELECT 
        i.nome AS institution_name,
        d.nome AS illness_name,
        COUNT(DISTINCT d.id) AS num_different_illnesses,
        SUM(c.internamentos) AS total_internamentos,
        MAX(c.diasInternamento) AS max_dias_internamento,
        SUM(c.ambulatorio) AS total_ambulatorio,
        SUM(c.obitos) AS total_obitos
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
    return render_template('listar_clinicstats.html', clinicstats=clinicstats)

@APP.route('/Regiao/')
def regiao():
    # Obtém quantos hospitais ha numa regiao numero no relatorio?????
    regiao = db.execute('''
        SELECT regiao, COUNT(nome) AS n_hospitais 
        FROM Instituicao 
        GROUP BY regiao
    ''').fetchall()
    return render_template('regiao.html', Regiao=regiao)

@APP.route('/Instituicao/<String:nome>/')
def instituicao():
    # Obtém clinicstats por hospital
    instituicao = db.execute('''
        SELECT i.nome, COUNT(c.ID) AS n_reports 
        FROM Instituicao i
        NATURAL JOIN ClinicStats c
        GROUP BY nome
    ''').fetchall()
    return render_template('instituicao.html',
                            Instituicao=instituicao)

@APP.route('/Diagnostico/')
def diagnostico():
    # Quais diagnosticos possuem mais óbitos, internaçoes e ambulatórios
    diagnostico = db.execute('''
        SELECT ID, nome, sum(obitos) AS Obitos, sum(internamentos) AS Internamentos, sum(ambulatorio) AS Ambulatório, sum(diasInternamento) AS diasInternamento 
        FROM Diagnostico 
        NATURAL JOIN ClinicStats 
        GROUP BY ID 
        ORDER BY Obitos DESC, Internamentos, Ambulatório, diasInternamento
    ''').fetchall()
    return render_template('diagnostico.html',
                            Diagnostico=diagnostico)

@APP.route('/Regiao_Diagnostico/')
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
    return render_template('r_diagnostico.html',
                            Diagnostico=diagnostico)

@APP.route('/Obitos_Instituicao/')
def o_instituicao():
    # Quais hospitais, regiões e diagnosticos possuem mais obitos
    o_instituicao = db.execute('''
        SELECT i.nome AS Hospitais, r.nome AS Regiao,d.nome AS Diagnostico, p.data AS Data, COUNT(DISTINCT c.obitos) AS Obitos
        FROM ClinicStats c
        JOIN Instituicao i ON c.instituicao = i.nome
        JOIN Regiao r ON i.regiao = r.nome
        JOIN Periodo p ON c.data = p.data
        JOIN Diagnostico d ON c.ID = d.ID
        GROUP BY r.nome, c.data, i.nome
        ORDER BY r.nome, c.data, Obitos DESC; ---- demora muito stempo temos que as dividir em partes 
    ''').fetchall()
    return render_template('o_instituicao.html',
                           Obitos=o_instituicao)

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
    return render_template('d_hospital.html',
                                Diagnostico=diagnostico)

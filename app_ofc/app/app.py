import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from flask import render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
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
    # 
    clinicstats = db.execute('''
        SELECT c.data, i.instituicao, d.nome, c.internamentos, c.diasInternamento, c.ambulatorio, c.obitos
        FROM ClinicStats c
        JOIN Diagnostico d ON c.diagnostico_id = d.id
        JOIN Instituicao i ON c.instituicao_id = i.id
        ORDER BY c.data DESC, i.instituicao
    ''').fetchall()
    return render_template('listar_clinicstats.html', ClinicStats=clinicstats)

@APP.route('/Regiao/')
def regiao():
    # Obtém quantos hospitais ha numa regiao
    regiao = db.execute('''
        SELECT regiao, COUNT(nome) AS n_hospitais 
        FROM Instituicao 
        GROUP BY regiao
    ''').fetchall()
    return render_template('regiao.html',
                            Regiao=regiao)

@APP.route('/Instituicao/<String:nome>/')
def instituicao():
    # Obtém clinicstats por hospital
    instituicao = db.execute('''
        SELECT i.nome, COUNT(c.ID) AS n_reports 
        FROM Instituicao i
        NATURAL JOIN ClinicStats
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
        SELECT i.nome AS Hospitais, r.nome AS Regiao,d.nome AS Diagnostico, p.data AS Data, COUNT(DISTINCT obitos) AS Obitos
        FROM ClinicStats c
        JOIN Instituicao i ON c.instituicao = i.nome
        JOIN Regiao r ON i.regiao = r.nome
        JOIN Periodo p ON c.data = p.data
        JOIN Diagnostico d
        WHERE obitos IS NOT NULL 
        GROUP BY r.nome, c.data, i.nome
        ORDER BY r.nome, c.data, Obitos DESC;
    ''').fetchall()
    return render_template('o_instituicao.html',
                           Obitos=o_instituicao)

@APP.route('/Pacientes_Internacao')
def p_interna():
    # Pacientes com diagnosticos que resultaram em internações superiores à média global
    p_internacoes = db.execute('''
        WITH AvgInt AS(
        SELECT AVG(c.internamentos) AS MedGlob, c.IDP AS IDP
        FROM ClinicStats c
        GROUP BY c.IDP)
        SELECT p.IDP AS Pacientes, d.nome AS Diagnostico, c.internamentos AS Internamentos, p.faixaEtaria AS Faixa_Etaria
        FROM ClinicStats c
        JOIN Paciente p ON c.IDP = p.IDP
        JOIN Diagnostico d ON c.ID = d.ID
        JOIN AvgInt ON c.IDP = AvgInt.IDP
        WHERE c.internamentos > AvgInt.MedGlob
        ORDER BY Faixa_Etaria, Diagnostico
    ''').fetchall()
    return render_template('p_internacoes.html',
                           Pacientes=p_internacoes)
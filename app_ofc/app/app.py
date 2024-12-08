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
            (SELECT COUNT(*) data FROM Periodo)
        JOIN
            (SELECT COUNT(*) internamentos FROM ClinicStats;)
        JOIN
            (SELECT COUNT(*) IDP FROM Paciente)
        JOIN
            (SELECT COUNT(*) ID FROM Diagnostico)
        JOIN
            (SELECT COUNT(*) nome FROM Instituicao)
        JOIN
            (SELECT COUNT(*) nome FROM Regiao)
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


####
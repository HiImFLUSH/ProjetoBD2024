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
    clinicstats = db.execute('''
        SELECT data, instituicao, diagnostico.nome, internamentos, diasInternamento, ambulatorio, obitos 
        FROM ClinicStats 
        NATURAL JOIN Diagnostico 
        ORDER BY data DESC, instituicao
    ''').fetchall()
    return render_template('listar_clinicstats.html', ClinicStats=ClinicStats)

@APP.route('/Regiao/')
def regiao():
    # Obtém quantos hospitais ha numa regiao
    regiao = db.execute('''
        SELECT regiao, COUNT(nome) AS n_hospitais 
        FROM Instituicao 
        GROUP BY regiao
    ''').fetchall()
    return render_template('regiao.html',
                            regiao=regiao)

@APP.route('/Diagnostico/')
def regiao():
    # Quais diagnosticos possuem mais óbitos, internaçoes e ambulatórios
    diagnostico = db.execute('''
        SELECT ID, nome, sum(obitos) AS Fatalidades, sum(internamentos) AS Internamentos, sum(ambulatorio) AS Ambulatório, sum(diasInternamento) AS diasInternamento 
        FROM Diagnostico 
        NATURAL JOIN ClinicStats 
        GROUP BY ID ORDER BY Fatalidades DESC, Internamentos, Ambulatório, diasInternamento
    ''').fetchall()
    return render_template('diagnostico.html',
                            diagnostico=diagnostico)

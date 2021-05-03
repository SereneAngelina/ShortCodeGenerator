from flask import Flask, request, abort, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

import re
import random
import string
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


@app.before_first_request
def create_tables():
    db.create_all()
    db.session.commit()


class Url(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    url = db.Column("url", db.String(255))
    short_code = db.Column("short_code", db.String(6))

    def __init__(self, url, short_code):
        self.url = url
        self.short_code = short_code


class Stats(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    short_code_id = db.Column("short_code_id", db.Integer, db.ForeignKey(Url.id))
    redirects_count = db.Column("redirects_count", db.Integer, default=0)
    year = db.Column("year", db.String(4))
    week = db.Column("week", db.String(2))

    def __init__(self, short_code_id, redirects_count, year, week):
        self.short_code_id = short_code_id
        self.redirects_count = redirects_count
        self.year = year
        self.week = week


year = datetime.strftime(datetime.today(), "%Y")
week = datetime.strftime(datetime.today(), "%V")


# Create shortcode for the given URL
@app.route('/create_short_url', methods=['POST'])
def short_url():
    if not request.json or 'url' not in request.json:
        abort(400, {'message': 'Url not present(required)'})
    url = request.json['url']

    if 'shortcode' not in request.json:
        code = string.digits + '_' + string.ascii_lowercase
        short_code = ''.join(random.choice(code) for i in range(6))
    else:
        short_code = request.json['shortcode']
        valid_code = re.match("^[A-Za-z0-9_]*$", short_code)
        if not bool(valid_code) or len(short_code) > 6:
            return {'message': 'Invalid ShortCode'}, 404

    code_check = Url.query.filter_by(short_code=short_code).first()
    if code_check:
        return {'message': 'Shortcode already in use'}, 409

    save_url = Url(url=url, short_code=short_code)
    db.session.add(save_url)
    db.session.commit()
    return {'shortcode': short_code}, 201


@app.route('/<short_code>', methods=['GET'])
def get_short_code(short_code):
    query_result = Url.query.filter_by(short_code=short_code).first_or_404()
    stats_result = Stats.query.filter_by(short_code_id=query_result.id).count()
    if stats_result == 0:
        stats_entry = Stats(short_code_id=query_result.id, redirects_count=1, week=week,
                            year=year)
        db.session.add(stats_entry)
        db.session.commit()
    else:
        result = Stats.query.filter_by(short_code_id=query_result.id, week=week).first()
        if result:
            result.redirects_count = result.redirects_count + 1
            db.session.commit()
    return redirect(query_result.url)


@app.route('/stats/<short_code>', methods=['GET'])
def get_stats(short_code):
    result = []
    query_result = Url.query.filter_by(short_code=short_code).first_or_404()
    stats_result = Stats.query.filter_by(short_code_id=query_result.id)
    for res in stats_result:
        stats = {"year": res.year,
                 "week": res.week,
                 "redirects_count": res.redirects_count}
        result.append(stats.copy())
    return {"stats": result}


@app.errorhandler(404)
def page_not_found(e):
    return {'message': 'Shortcode not found'}, 404


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)

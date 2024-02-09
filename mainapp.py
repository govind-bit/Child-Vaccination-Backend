from flask import Flask, request, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask_cors import CORS
import sqlalchemy.exc
from models import db,P_INFO,H_INFO,A_INFO


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///VFC.db'
db.init_app(app)

def generate_unique_token():
    return str(uuid.uuid4())

@app.route('/', methods=['GET'])
def index():
    print(session.get('logged_in'))
    if session.get('logged_in'):
        return jsonify({'status': 'success', 'token': session.get('token')})
    else:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 400

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json(force=True)
    role = data.get('role')
    mail = data.get('mail')
    password_hash = generate_password_hash(data.get('password'), method='pbkdf2:sha256') 
    security_q=data.get('security_q')
    security_ans=data.get('security_ans')
    try:
        if role == 'parent':
            p_name = data.get('p_name')
            address = data.get('address')
            contact = data.get('contact')
            #password_hash=generate_password_hash(data.get('password'), method='pbkdf2:sha256')
            db.session.add(P_INFO(
                MAIL=mail,
                PASSWORD=password_hash,
                P_NAME=p_name,
                ADDRESS=address,
                SECURITY_Q=security_q,
                SECURITY_ANS=security_ans,
                CONTACT=contact
            ))
        elif role == 'hospital':
            h_name = data.get('h_name')
            address = data.get('address')
            city = data.get('city')
            contact = data.get('contact')
            #password_hash=generate_password_hash(data.get('password'), method='pbkdf2:sha256')
            db.session.add(H_INFO(
                MAIL=mail,
                PASSWORD=password_hash,
                H_NAME=h_name,
                ADDRESS=address,
                CITY=city,
                CONTACT=contact,
                SECURITY_Q=security_q,
                SECURITY_ANS=security_ans
            ))
        else:
            return jsonify({'status': 'error', 'message': 'Invalid role'}), 400

        db.session.commit()
        return jsonify({'status': 'success'}), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'User name already exist'}), 400

@app.route('/login', methods=['POST'])
def login():
  
    data = request.get_json(force=True)
    role = data["role"]
    mail = data["mail"]
    password = data["password"]
    if role == "parent":
        user = P_INFO.query.filter_by(MAIL=mail).first()
    elif role == 'hospital':
        user = H_INFO.query.filter_by(MAIL=mail).first()
    elif role == 'admin':
        admin = A_INFO.query.filter_by(MAIL=mail).first()
        if admin and check_password_hash(admin.PASSWORD,password):
            session['logged_in'] = True
            session['token'] = generate_unique_token()
            return jsonify({'status': 'success', 'token': session['token']}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Incorrect admin details'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'Invalid role'}), 400
    if user and check_password_hash(user.PASSWORD,password) :
        session['logged_in'] = True
        session['token'] = generate_unique_token()
        return jsonify({'status': 'success', 'token': session['token']}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect details'}), 400


@app.route('/forgotpassword', methods=['POST'])
def forgot_password():
    data = request.json
    mail = data.get('mail')
    security_q = data.get('security_q')
    security_ans = data.get('security_ans')
    new_password = data.get('new_password')

    parent_user = P_INFO.query.filter_by(MAIL=mail).first()
    hospital_user = H_INFO.query.filter_by(MAIL=mail).first()
    

    if parent_user:
        user = parent_user
        
    elif hospital_user:
        user = hospital_user
    else:
        return jsonify({"error": "User not found"}), 404
  

    stored_security_question, stored_security_answer = user.SECURITY_Q, user.SECURITY_ANS
    

    if (str(stored_security_question) ==str(security_q)  )and (str(stored_security_answer) == str(security_ans)):

        user.PASSWORD = new_password #generate_password_hash(new_password, method='sha256')
        db.session.commit()
        return jsonify({"message": "Password updated successfully."}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.secret_key = "ThisIsNotASecret:p"
    app.run(debug=True)


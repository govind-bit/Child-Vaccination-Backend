from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from modles import *
import datetime
import sqlalchemy.exc
#______________________________________________________________

parent_bp = Blueprint('parent', __name__)

#_______________________________________________________________

@parent_bp.route('/add_child/<p_mail>', methods=['POST'])
def add_child(p_mail):
    # Parse JSON data from the request
    data = request.get_json()
    
    # Extract child's information from the data
    c_name = data.get('c_name')
    age = data.get('age')
    dob_str = data.get('dob')
    dob = datetime.datetime.strptime(dob_str, '%Y-%m-%d').date()

    gender = data.get('gender')
    blood_type = data.get('blood_type')
    
    # Create a new instance of C_INFO with the extracted data
    try:
        parent = P_INFO.query.filter_by(MAIL=p_mail).first()
        print(parent)
        if parent is None:
            # Parent email does not exist, return an error response
            return jsonify({'error': 'Parent email does not exist'}), 400
        child = C_INFO(
        C_NAME=c_name,
        AGE=age,
        DOB=dob,
        GENDER=gender,
        BLOOD_TYPE=blood_type,
        P_MAIL=p_mail  
    )
    # Add the new child instance to the database session and commit the transaction
        db.session.add(child)
        db.session.commit()
    
    # Return a JSON response indicating success
        return jsonify({'status': 'success', 'child_id': child.C_ID}), 200
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'User name already exist'}), 400

#________________________________________________________________________________________________________________

@parent_bp.route('/delete_child/<child_id>', methods=['DELETE'])
def delete_child(child_id):
    try:
        # Query the child by ID and delete it
        child = C_INFO.query.filter_by(C_ID=child_id).first()
        if child:
            db.session.delete(child)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Child deleted successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Child not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error deleting child: {str(e)}'}), 500

#___________________________________________________________________________________________________________________________

@parent_bp.route('/update_child/<p_mail>/<child_id>', methods=['POST'])
def update_child(p_mail, child_id):
    # Get the data from the request form
    data = request.form 
    new_child_name = data.get('new_child_name')
    new_age = data.get('new_age')
    new_dob_str = data.get('new_dob')
    new_gender = data.get('new_gender')
    new_blood_type = data.get('new_blood_type')

    # Check if the parent exists
    parent = P_INFO.query.filter_by(MAIL=p_mail).first()
    if not parent:
        return jsonify({'status': 'error', 'message': 'Parent not found'}), 404

    # Check if the child exists
    child = C_INFO.query.filter_by(P_MAIL=p_mail, C_ID=child_id).first()
    if not child:
        return jsonify({'status': 'error', 'message': 'Child not found'}), 404

    try:
        # Update child's information
        if new_child_name:
            child.C_NAME = new_child_name
        if new_age:
            child.AGE = int(new_age)  # Convert to integer
        if new_dob_str:
            new_dob = datetime.strptime(new_dob_str, '%Y-%m-%d').date()
            child.DOB = new_dob
        if new_gender:
            child.GENDER = new_gender
        if new_blood_type:
            child.BLOOD_TYPE = new_blood_type

        db.session.commit()

        # Return success message
        return jsonify({'status': 'success', 'message': 'Child information updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        # Return error message
        return jsonify({'status': 'error', 'message': f'Error updating child: {str(e)}'}), 400
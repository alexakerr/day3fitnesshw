from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
# local import for db connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.json.sort_keys = False #maintain order of your stuff

ma = Marshmallow(app)


class MemberSchema(ma.Schema):
    member_id = fields.Int(dump_only=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    membership_type = fields.String(required=True)


    class Meta:  
        
        fields = ("member_id", "name", "email", "phone", "membership_type")
customer_schema = MemberSchema()
customers_schema = MemberSchema(many=True)

@app.route('/')
def home():
    return "Welcome to our super cool Fitness Tracker, time to get fit !"

@app.route('/customers', methods=['GET'])
def get_customers(): 
    print("hello from the get")  
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Customer"

        cursor.execute(query)
        customers = cursor.fetchall()

        return customers_schema.jsonify(customers)
    
    except Error as e:
        print(f"Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()



#update
@app.route('/members/<int:member_id>', methods= ["PUT"])
def update_member(member_id):
    try:
        member_data = MemberSchema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400
    
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        query = "UPDATE MEMBERS SET date = %s, memborship_type = %s WHERE membership_id = %s"
        cursor.execute(query, (member_data['date'], member_data['membership_id'],))
        conn.commit()
        return jsonify({"message": "Order updated succesfully"}), 200    


    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    
# DELETE Request
@app.route("/members/<int:membership_id>", methods=["DELETE"])
def delete_member(membership_id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = "SELECT * FROM Orders WHERE membership_id = %s"
        cursor.execute(query, (membership_id,))
        member = cursor.fetchone()
        if not member:
            return jsonify({"error": "Memborship does not exist"}), 404
        
        del_query = "DELETE FROM Members where membership_id = %s"
        cursor.execute(del_query, (membership_id,))
        conn.commit()
        return jsonify({"message": f"Succesfully delete member_id {membership_id}"})     

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

















if __name__ == "__main__":
    app.run(debug=True)

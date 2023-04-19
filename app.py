from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# set up an api with get and post request
app = Flask(__name__)
api = Api(app)
CORS(app)
# set up the database with sqlite
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ('database_link') or "postgresql://somelink"

db = SQLAlchemy(app)


all_results_fields = {
    "id": fields.Integer,
    "checked": fields.Integer,
    "unchecked": fields.Integer,
    "responses": fields.Integer
}

class ResultsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checked = db.Column(db.Integer, nullable=False)
    unchecked = db.Column(db.Integer, nullable=False)
    responses = db.Column(db.Integer, nullable=False)

# db.create_all()


task_post_args = reqparse.RequestParser()
task_post_args.add_argument('results', type=dict, required=True, help="No results are provided")


class AllResults(Resource):
    @marshal_with(all_results_fields)
    def get(self):
        return ResultsModel.query.all()

    @marshal_with(all_results_fields)
    def post(self):
        args = task_post_args.parse_args()
        # results looks like {1: true, 2: false, 3: false}, questionNum: isChecked
        results = args['results']
        score = 0

        if len(results) != 101:
            return abort(400, message="You must provide all 101 questions")


        for questionNum in results.keys():
            try:
                intQuestionNum = int(questionNum)
            except:
                abort(400, message=f"Question numbers must be integers, {questionNum} is not an integer")
            
            if type(intQuestionNum) != int:
                abort(400, message="Question {} doesn't exist".format(questionNum))
            if type(results[questionNum]) != bool:
                abort(400, message="isChecked value {} is not a boolean".format(results[questionNum]))
            if intQuestionNum < 1 or intQuestionNum > 101:
                abort(400, message="Question {} doesn't exist".format(questionNum))
        

        for questionNum in results.keys():
            intQuestionNum = int(questionNum)
            result = ResultsModel.query.filter_by(id = intQuestionNum).first()
            if not result:


                result = ResultsModel(id=intQuestionNum, checked=0, unchecked=0, responses=0)
                db.session.add(result)
                db.session.commit()
            
            if results[questionNum]:
                result.checked += 1
                score += 1
            else:
               result.unchecked += 1
            result.responses += 1

        db.session.commit()
        return ResultsModel.query.all(), 201
        

class Results(Resource):
    @marshal_with(all_results_fields)
    def get(self, result_id):
        result = ResultsModel.query.filter_by(id = result_id).first()
        if not result:
            abort(404, message="Question {} doesn't exist".format(result_id))
        return result


    

api.add_resource(Results, '/results/<int:result_id>')
api.add_resource(AllResults, '/results/')


if __name__ == '__main__':
    
    app.run(debug=True)
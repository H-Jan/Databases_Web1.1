from flask import Flask, request, redirect, render_template, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

############################################################
# SETUP
############################################################

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/plantsDatabase"
mongo = PyMongo(app)

############################################################
# ROUTES
############################################################

@app.route('/')
def plants_list():
    """Display the plants list page."""

    plants_data = mongo.db.plants.find()
    #Leaving blank should find all

    context = {
        'plants': plants_data,
    }
    return render_template('plants_list.html', **context)

@app.route('/about')
def about():
    """Display the about page."""
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Display the plant creation page & process data from the creation form."""
    if request.method == 'POST':
        new_plant = {
            'name': request.form.get('plant_name'),
            'variety': request.form.get('variety'),
            'photo_url': request.form.get('photo'),
            'date_planted': request.form.get('date_planted')
        }
        # TODO: Make an `insert_one` database call to insert the object into the
        # database's `plants` collection, and get its inserted id. Pass the 
        # inserted id into the redirect call below.
        insert_object = mongo.db.plants.insert_one(new_plant)

        return redirect(url_for('detail', plant_id=insert_object.inserted_id)

    else:
        return render_template('create.html')

@app.route('/plant/<plant_id>')
def detail(plant_id):
    """Display the plant detail page & process data from the harvest form."""

    plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

    harvests = mongo.db.plants.find({'plant_id': ObjectId(plant_id)})

    context = {
        'plant' : plant_to_show,
        'harvests': harvests
    }
    return render_template('detail.html', **context)

@app.route('/harvest/<plant_id>', methods=['POST'])
def harvest(plant_id):
    """
    Accepts a POST request with data for 1 harvest and inserts into database.
    """
    harvested_amount = request.form.get('harvested_amount')
    date_planted = request.form.get('date_planted')

    new_harvest = {
        'quantity': harvested_amount,
        'date': date_planted,
        'plant_id': plant_id
    }

    mongo.db.harvest.insert_one(new_harvest)

    return redirect(url_for('detail', plant_id=plant_id))

@app.route('/edit/<plant_id>', methods=['GET', 'POST'])
def edit(plant_id):
    """Shows the edit page and accepts a POST request with edited data."""

    #Clean up first, its getting complicated
    updated_name = request.form.get('plant_name')
    updated_variety = request.form.get('variety')
    updated_photo_url = request.form.get('photo')
    updated_date_planted = request.form.get('date_planted')

    if request.method == 'POST':
        
        mongo.db.plants.update_one(
            {'_id': ObjectId(plant_id)},
            #change id
            { 
                '$set': 
                {
                    'name': updated_name,
                    'variety': updated_variety,
                    'photo_url': updated_photo_url,
                    'date_planted': updated_date_planted
                }

            }
        )
        
        return redirect(url_for('detail', plant_id=plant_id))
    else:
        plant_to_show = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})

        context = {
            'plant': plant_to_show
        }

        return render_template('edit.html', **context)

@app.route('/delete/<plant_id>', methods=['POST'])
def delete(plant_id):
    #Delete one
    mongo.db.plants.delete_one({ '_id': ObjectId(plant_id)})

    #Delete Many
    mongo.db.plants.delete_many({})
    

    return redirect(url_for('plants_list'))

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, render_template

app = Flask(__name__)

sample_data = {
        'username': 'someguy',
        'comments': [
            {
                'link_name': 'title of link from api',
                'link_id': 't1_foo',
                'body':'first post',
                'day':1,
                'ups': 7,
                'downs': 2,
                'responses':
                [
                    {
                        'body':'first response',
                        'ups': 1,
                        'downs': 0
                    },
                    {
                        'body':'second response',
                        'ups': 3,
                        'downs': 5
                    }
                ]
            }
        ]
    }

@app.route('/')
def home():
    return 'Try /singleposter or /multiposter'

@app.route('/style.css')
def stylesheet():
    return render_template('style.css')

@app.route('/singleposter')
def single_poster():

    return render_template('user.html',
        data=sample_data)

if __name__ == '__main__':
    app.run(debug=True)

from pyspark import SparkContext
from pyspark.sql import HiveContext

sc = SparkContext('local[4]', 'RedditPivot')
sql = HiveContext(sc)

#comments = sql.read.json('s3n://%s:%s@boazreddit/micro_fake.json' % (os.environ['AWS_ACCESS_KEY'], os.environ['AWS_SECRET_KEY']))
comments = sql.read.json('data/RC_2015-01')

pivot = sql.sql('''SELECT
                        author,
                        MIN(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS first_post,
                        MAX(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS last_post,
                        COUNT(*) AS total_posts
                   FROM comments
                   GROUP BY author
                   HAVING total_posts>1''')
#pivot.cache()

# pivot2 = sql.sql('''SELECT author, COLLECT_SET(body) AS posts
#                     FROM comments
#                     WHERE author='fake_author1'
#                     GROUP BY author''')


pivot.toJSON().saveAsTextFile('users')
#comments.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/outtest' % (os.environ['AWS_ACCESS_KEY'], os.environ['AWS_SECRET_KEY']))

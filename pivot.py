from pyspark import SparkContext
from pyspark.sql import HiveContext
import os

acc = os.environ['AWS_ACCESS_KEY_ID']
sec = os.environ['AWS_SECRET_ACCESS_KEY']

sc = SparkContext() # 'local[4]', 'RedditPivot')
sqlContext = HiveContext(sc)

#comments = sqlContext.read.json('data/test/*/')
#comments = sqlContext.read.json('s3n://%s:%s@boazreddit/micro_fake.json' % (acc, sec))
#comments = sqlContext.read.json('s3n://%s:%s@boazreddit/test/*/*' % (acc, sec))
#comments = sqlContext.read.json('s3n://%s:%s@boazreddit/comments/2007/*' % (acc, sec))
comments = sqlContext.read.json('s3n://%s:%s@boazreddit/comments/200*/*' % (acc, sec))
#comments = sqlContext.read.json('s3n://%s:%s@boazreddit/comments/*/*' % (acc, sec))

comments.registerTempTable('comments')
sqlContext.cacheTable('comments')

users = sqlContext.sql('''SELECT
                    comments.author AS author,
                    comments.id AS first_post_id,
                    comments.body AS first_post_body,
                    comments.subreddit AS first_post_subreddit,
                    comments.ups AS first_post_ups,
                    comments.downs AS first_post_downs,
                    comments.link_id AS first_post_link_id,
                    responses.responses AS first_post_responses,
                    responses.response_ups AS first_post_response_ups,
                    responses.response_downs AS first_post_response_downs,
                    responses.total_responses AS first_post_total_responses,
                    responses.avg_response_ups AS first_post_avg_response_ups,
                    responses.avg_response_downs AS first_post_avg_response_downs,
                    SUBSTR(comments.parent_id, 1, 2) AS parent_type,
                    user_pivot.first_post_datetime AS first_post_datetime,
                    user_pivot.last_post_datetime AS last_post_datetime,
                    user_pivot.post_ids AS post_ids,
                    user_pivot.post_datetimes AS post_datetimes,
                    user_pivot.subreddits AS subreddits,
                    user_pivot.total_subreddits AS total_subreddits,
                    user_pivot.total_posts AS total_posts
                    FROM comments
                    JOIN
                        (SELECT
                            author,
                            MIN(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS first_post_datetime,
                            MAX(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS last_post_datetime,
                            COLLECT_LIST(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS post_datetimes,
                            COLLECT_LIST(id) AS post_ids,
                            COLLECT_LIST(subreddit) AS subreddits,
                            COUNT(DISTINCT(subreddit)) AS total_subreddits,
                            COUNT(*) AS total_posts
                       FROM comments
                       GROUP BY author) user_pivot
                    ON comments.author=user_pivot.author
                        AND CAST((FROM_UNIXTIME(INT(comments.created_utc))) AS TIMESTAMP)=user_pivot.first_post_datetime
                    LEFT OUTER JOIN
                       (SELECT
                            parent_id,
                            COLLECT_LIST(body) AS responses,
                            COLLECT_LIST(ups) AS response_ups,
                            COLLECT_LIST(downs) AS response_downs,
                            COUNT(*) AS total_responses,
                            AVG(ups) AS avg_response_ups,
                            AVG(downs) AS avg_response_downs
                        FROM
                            comments
                        GROUP BY
                            parent_id) responses
                        ON comments.id=SUBSTR(responses.parent_id,4)''')

users.registerTempTable('users')

#users.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/users' % (acc,sec))
#users.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/users2007' % (acc, sec))
users.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/users2000s' % (acc, sec))

sc.stop()



###### Subquery Tests ######

# WORKS
# responses = sqlContext.sql('''SELECT
#                             parent_id AS full_parent_id,
#                             SUBSTR(parent_id,4) AS short_parent_id,
#                             COLLECT_LIST(body) AS responses,
#                             COLLECT_LIST(ups) AS response_ups,
#                             COLLECT_LIST(downs) AS response_downs,
#                             COUNT(*) AS total_responses,
#                             AVG(ups) AS avg_response_ups,
#                             AVG(downs) AS avg_response_downs
#                         FROM
#                             comments
#                         GROUP BY
#                             parent_id
#                         HAVING
#                             total_responses>1
#                             ''')
#
# responses.registerTempTable('responses')
# responses.toJSON().saveAsTextFile('responses_test')

# WORKS
# user_pivot = sqlContext.sql('''SELECT
#                             author,
#                             MIN(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS first_post_datetime,
#                             MAX(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS last_post_datetime,
#                             COLLECT_LIST(CAST((FROM_UNIXTIME(INT(created_utc))) AS TIMESTAMP)) AS post_datetimes,
#                             COLLECT_LIST(id) AS post_ids,
#                             COLLECT_LIST(body) AS posts,
#                             COLLECT_LIST(ups) AS ups,
#                             COLLECT_LIST(downs) AS downs,
#                             COLLECT_LIST(link_id) AS link_ids,
#                             COLLECT_LIST(parent_id) AS parent_ids,
#                             COUNT(DISTINCT(subreddit)) AS total_subreddits,
#                             COLLECT_LIST(subreddit) AS subreddits,
#                             COUNT(*) AS total_posts
#                        FROM comments
#                        GROUP BY author
#                        HAVING total_posts>1''')
#
# user_pivot.registerTempTable('user_pivot')
# user_pivot.toJSON().saveAsTextFile('user_pivot_test')

# Sample size
#
# 1 sample        1 total     .7 multi
# ----------   *  --------- * --------
# 400 total      .7 multi    .3 single
#
# .0013 total
# .0036 multi
# .0083 single

from pyspark import SparkContext, SparkConf
from pyspark.sql import HiveContext
import os

sp_conf = SparkConf()
sp_conf.setAppName('PoliticoSampler')
sp_conf.set('spark.driver.memory', '3g')

sc = SparkContext(conf=sp_conf) #'local[4]', 'PoliticoExplorer')
sqlContext = HiveContext(sc)

acc = os.environ['AWS_ACCESS_KEY_ID']
sec = os.environ['AWS_SECRET_ACCESS_KEY']

politicos = sqlContext.read.json('s3n://%s:%s@boazreddit/politicos/part-00000' % (acc, sec))
politicos.cache()

politicos.registerTempTable('politicos')
politicos_mixed_post = politicos.sample(False, 0.001)
politicos_mixed_post.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/politicos_mixed_sample' % (acc, sec))
politicos_single_post = politicos.filter(politicos.total_posts==1).sample(False, 0.0083)
politicos_single_post.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/politicos_single_sample' % (acc, sec))
politicos_multi_post = politicos.filter(politicos.total_posts>1).sample(False, 0.0036)
politicos_multi_post.toJSON().saveAsTextFile('s3n://%s:%s@boazreddit/politicos_multi_sample' % (acc, sec))

sc.stop()

from pyspark import SparkContext, SparkConf
import os

sp_conf = SparkConf()
sp_conf.setAppName('PoliticoSampler')
sp_conf.set('spark.driver.memory', '4g')
sc = SparkContext(conf=sp_conf) #'local[4]', 'PoliticoExplorer')

numPartitions = 16

# Read full dataset of Reddit Politics users
#politicos_read = sc.textFile('data/politicos/full')
politicos_read = sc.textFile('s3n://boazreddit/politicos')
politicos = politicos_read.repartition(numPartitions)

# Downsample to 10% (max recommended for statistical inference)
politicos_mixed_sample = politicos.sample(False, 0.10)

# Label (single/multi) and calculate counts for balancing sample
def single_post(line):
    return '"total_posts":1' in line
politicos_single_multi = politicos_mixed_sample.map(lambda line: (single_post(line), line))
politicos_single_multi.cache()
total_count = politicos_single_multi.count()
single_count = politicos_single_multi.filter(lambda (single_post_status, line): single_post_status).count()
multi_count = total_count - single_count

# Balance samples
# Ex: multi=0.7, single=0.3
# single_sample_rate=1
# multi_sample_rate = 0.3/0.7
if multi_count >= single_count:
    multi_sample_rate = single_count * 1.0 / multi_count
    politicos_multi_post = politicos_single_multi \
                               .filter(lambda (single_post_status, line): not single_post_status) \
                               .sample(False, multi_sample_rate) \
                               .map(lambda (single_post_status, line): line)
    # keep all single posts
    politicos_single_post = politicos_single_multi \
                               .filter(lambda (single_post_status, line): single_post_status) \
                               .map(lambda (single_post_status, line): line)

else: # single_count > multi_count
    single_sample_rate = multi_count * 1.0 / single_count
    politicos_single_post = politicos_single_multi \
                               .filter(lambda (single_post_status, line): single_post_status) \
                               .sample(False, single_sample_rate) \
                               .map(lambda (single_post_status, line): line)
    # keep all multi posts
    politicos_multi_post = politicos_single_multi \
                               .filter(lambda (single_post_status, line): not single_post_status) \
                               .map(lambda (single_post_status, line): line)

# Write results
politicos_single_post.saveAsTextFile('s3n://boazreddit/politicos_single_sample_balanced')
#politicos_single_post.saveAsTextFile('data/politicos/politicos_single_sample_large')
politicos_multi_post.saveAsTextFile('s3n://boazreddit/politicos_multi_sample_balanced')
#politicos_single_post.saveAsTextFile('data/politicos/politicos_single_sample_large')

sc.stop()


# Sample size
#
# 1 sample        1 total     .7 multi
# ----------   *  --------- * --------
# 400 total      .7 multi    .3 single
#
# .0013 total  *12 = 0.0156
# .0036 multi  *12 = 0.0432
# .0083 single *12 = 0.0996

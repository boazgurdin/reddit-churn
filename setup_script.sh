# Set AWS credentials
export AWS_ACCESS_KEY_ID=AKIAIUD55SX7VWBAZ7AA
export AWS_SECRET_ACCESS_KEY=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

# Update AWS CLI
yum update aws-cli

# Install all the necessary packages on Master

yum install -y tmux
yum install -y pssh
yum install -y python27 python27-devel
yum install -y freetype-devel libpng-devel
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python27
easy_install-2.7 pip
easy_install py4j

pip2.7 install ipython==2.0.0
pip2.7 install pyzmq==14.6.0
pip2.7 install jinja2==2.7.3
pip2.7 install tornado==4.2

pip2.7 install numpy
pip2.7 install matplotlib
pip2.7 install nltk
ipython -c "import nltk; nltk.download('all')"

# Install all the necessary packages on Workers

pssh -h /root/spark-ec2/slaves yum install -y python27 python27-devel
pssh -h /root/spark-ec2/slaves "wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python27"
pssh -h /root/spark-ec2/slaves easy_install-2.7 pip
pssh -t 10000 -h /root/spark-ec2/slaves pip2.7 install numpy
pssh -h /root/spark-ec2/slaves pip2.7 install nltk

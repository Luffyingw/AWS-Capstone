Step 1: Set up Kafka on AWS
using cloudFormation file in github

Step 2: Spin up an EMR 5.0 cluster with Hadoop, Hive, and Spark
```
aws emr create-cluster \
     --name Blogreplay \
     --release-label emr-5.0.0 \
     --instance-groups InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m3.xlarge InstanceGroupType=CORE,InstanceCount=2,InstanceType=m3.xlarge \
     --service-role EMR_DefaultRole \
     --ec2-attributes InstanceProfile=EMR_EC2_DefaultRole,SubnetId=subnet-XXX,KeyName=XXX \
     --log-uri s3://XXX \
     --enable-debugging \
     --no-auto-terminate \
     --visible-to-all-users \
     --applications Name=Hadoop Name=Hive Name=Spark \
     --region XXX
```

you can select instanceType. Replace subnetId, s3 path, keyName is your pem file, select region

How to create public subnet. Reference to Homework 1 in my repo.


Step 3: Create a Kafka topic
```
ssh -i "XXX.pem" ec2-user@<<zookeeperinstanceDNS>>
```

```
cd /app/kafka/kafka_2.9.2-0.8.2.1/bin

./kafka-server-start.sh ../config/server.properties
./zookeeper-server-start.sh ../config/zookeeper.properties 

./kafka-topics.sh --zookeeper ec2-54-157-253-86.compute-1.amazonaws.com:2181 --create --topic blog-replay --partitions 2 --replication-factor 1

./kafka-topics.sh --zookeeper ec2-54-157-253-86.compute-1.amazonaws.com:2181 --list
```



```
aws s3 cp kafkaandsparkstreaming-0.0.1-SNAPSHOT-jar-with-dependencies.jar s3://tutorial-cs502-bucket/

scp -i "XXX.pem" kafkaandsparkstreaming-0.0.1-SNAPSHOT-jar-with-dependencies.jar ec2-user@<<KafkaBrokerDNS>>:

ssh -i "XXX.pem" ec2-user@<<zookeeperinstanceDNS>>

 scp -i ~/XXX.pem ~/Downloads/kafkaandsparkstreaming-0.0.1-SNAPSHOT-jar-with-dependencies.jar ec2-user@54.236.216.53:
```



Step 4: Run the Spark Streaming app to process clickstream events
```
aws emr add-steps --cluster-id XXX \
--steps Type=spark,Name=SparkstreamingfromKafka,Args=--deploy-mode,cluster,--master,yarn,--num-executors,3,--executor-cores,3,--executor-memory,3g,--class,com.awsproserv.kafkaandsparkstreaming.ClickstreamSparkstreaming,s3://XXX/kafkaandsparkstreaming-0.0.1-SNAPSHOT-jar-with-dependencies.jar,ec2-XXX.compute-1.amazonaws.com:9092,blog-replay,ActionOnFailure=CONTINUE
```

replace clusterId, S3 path, KafkaBrokerDNS, 


Step 5: Use the Kafka producer app to publish clickstream events into the Kafka topic

```
java -cp kafkaandsparkstreaming-0.0.1-SNAPSHOT-jar-with-dependencies.jar com.awsproserv.kafkaandsparkstreaming.ClickstreamKafkaProducer 25 blog-replay localhost:9092
```



Step 6: Explore clickstream event data with SparkSQL
```
ssh -i ~/yourKey.pem hadoop@<<MasterNodeDNS>>
select * from csmessages_hive_table limit 10;
```
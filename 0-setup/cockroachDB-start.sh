# - # - # - # - # - # - # - # - # - # - # - #
#
#   SETTING UP COCKROACHDB CLUSTER: Starting it up!
#   (4 nodes)
#
# - # - # - # - # - # - # - # - # - # - # - #

# - 1 - Install CockroachDB on your local machine

# - 2 - Launch the 4 cluster instances

# - 3 - Create a cluster security group and add the instances 

# - 4 - Set up time sync on each node
sudo apt update
sudo apt install chrony

# here we'll open a file...
sudo nano /etc/chrony/chrony.conf
# ...and paste the following text above any pool or server statements
# -> server 169.254.169.123 prefer iburst minpoll 4 maxpoll 4
sudo /etc/init.d/chrony restart

# verify that chrony is using the 169.254.169.123 IP address 
#   to synchronize the time
chronyc sources -v

# verify the time synchronization metrics that are reported by chrony
chronyc tracking

# - 5 - Set up load balancing

# - 6 - GENERATE CERTIFICATES AND KEYS FOR EACH NODE

# - 7 - INSTALL AND START COCKROACHDB ON EACH NODE

# 7.1 CDB installation for node 1
ssh ubuntu@$CDB_NODE1_PUBLIC_IP_DNS 
wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.2.linux-amd64.tgz | tar xvz

# --- copy binary into the `PATH`
sudo cp -i cockroach-v19.2.2.linux-amd64/cockroach /usr/local/bin/

# --- run the `cockroach start` command, priming the node to start
cockroach start \
  --certs-dir=certs \
  --store=node1-data \
  --advertise-addr=$CDB_NODE1_PRIVATE_IP \
  --join=$CDB_NODE2_PRIVATE_IP \
  --join=$CDB_NODE3_PRIVATE_IP \
  --join=$CDB_NODE4_PRIVATE_IP \
  --cache=.25 \
  --max-sql-memory=.25 \
  --background

# 7.2 CDB installation for node 2
ssh ubuntu@$NODE2_PUBLIC_IP_DNS 
wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.2.linux-amd64.tgz | tar xvz

# --- copy binary into the `PATH`
sudo cp -i cockroach-v19.2.2.linux-amd64/cockroach /usr/local/bin/

# --- run the `cockroach start` command, priming the node to start
cockroach start \
  --certs-dir=certs \
  --store=node2-data \
  --advertise-addr=$CDB_NODE2_PRIVATE_IP \
  --join=$CDB_NODE1_PRIVATE_IP \
  --join=$CDB_NODE3_PRIVATE_IP \
  --join=$CDB_NODE4_PRIVATE_IP \
  --cache=.25 \
  --max-sql-memory=.25 \
  --background  

# 7.3 CDB installation for node 3
ssh ubuntu@$NODE3_PUBLIC_IP_DNS 
wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.2.linux-amd64.tgz | tar xvz

# --- copy binary into the `PATH`
sudo cp -i cockroach-v19.2.2.linux-amd64/cockroach /usr/local/bin/

# --- run the `cockroach start` command, priming the node to start
cockroach start \
  --certs-dir=certs \
  --store=node3-data \
  --advertise-addr=10.0.0.4$CDB_NODE3_PRIVATE_IP \
  --join=$CDB_NODE1_PRIVATE_IP \
  --join=$CDB_NODE2_PRIVATE_IP \
  --join=$CDB_NODE4_PRIVATE_IP \
  --cache=.25 \
  --max-sql-memory=.25 \
  --background  

# 7.4 CDB installation for node 4
ssh ubuntu@$NODE4_PUBLIC_IP_DNS 
wget -qO- https://binaries.cockroachdb.com/cockroach-v19.2.2.linux-amd64.tgz | tar xvz

# --- copy binary into the `PATH`
sudo cp -i cockroach-v19.2.2.linux-amd64/cockroach /usr/local/bin/

# --- run the `cockroach start` command, priming the node to start
cockroach start \
  --certs-dir=certs \
  --store=node4-data \
  --advertise-addr=$CDB_NODE4_PRIVATE_IP \
  --join=$CDB_NODE1_PRIVATE_IP \
  --join=$CDB_NODE2_PRIVATE_IP \
  --join=$CDB_NODE3_PRIVATE_IP \
  --cache=.25 \
  --max-sql-memory=.25 \
  --background      


# - 8 - INITIALIZE THE CLUSTER FROM WITHIN ANY OF ITS NODES
ssh ubuntu@$CDB_NODE1_PUBLIC_IP_DNS 
cockroach init --certs-dir=certs --host=$CDB_NODE1_PRIVATE_IP

# CLUSTER IS READY FOR USE!

# - 9 - CREATE A USER to ACCESS ADMINUI
#       (or any other users)

# SSH into the instance where you uploaded the client cert & key
ssh ubuntu@$WEBUI_PUBLIC_IP_DNS

# launch Cockroach SQL client
cockroach sql --certs-dir=certs --host=$CDB_BALANCER_PRIVATE_IP

# show all existing users... only the root user exists
SHOW USERS; 

# so we will alter the password of this user
CREATE USER brian WITH PASSWORD $CDB_BRIAN_PW;

# while we're here, initialize our new database
CREATE DATABASE era5;
GRANT ALL ON DATABASE fedspend TO brian;
SHOW DATABASES;

# logout
\q

# - OTHER: Decommissioning a node
# - it's expensive to keep all four nodes going 
cockroach quit --decommission --certs-dir=certs --host=<private IP of node>

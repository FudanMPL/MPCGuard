SCRIPT_PATH="${BASH_SOURCE:-$0}"
ABS_DIRECTORY="$(dirname "${SCRIPT_PATH}")"

kill -9 `ps -ef | grep tf_encrypted.player | grep -v grep | awk '{print $2}'`
kill -9 `ps -ef | grep ${ABS_DIRECTORY}/run.py | grep -v grep | awk '{print $2}'`

echo "Starting server0"
(python -m tf_encrypted.player server0 --config ${ABS_DIRECTORY}/rss_config.json > log_server_0.txt 2>&1 &)
sleep 1
echo "Starting server1"
(python -m tf_encrypted.player server1 --config ${ABS_DIRECTORY}/rss_config.json > log_server_1.txt 2>&1 &)
sleep 1
echo "Starting server2"
(python -m tf_encrypted.player server2 --config ${ABS_DIRECTORY}/rss_config.json > log_server_2.txt 2>&1 &)
sleep 1
echo "Starting inputter-0"
(python -m tf_encrypted.player inputter-0 --config ${ABS_DIRECTORY}/rss_config.json > log_inputer_0.txt 2>&1 &)
sleep 1
echo "Starting result-receiver"
(python -m tf_encrypted.player result-receiver --config ${ABS_DIRECTORY}/rss_config.json > log_receiver.txt 2>&1 &)
sleep 1

# echo "Run private average example..."
# (time python ${ABS_DIRECTORY}/test_rss_mul.py $* > log_master.txt 2>&1 &)

set -x

FRAMEWORKS=("CrypTen" "tf-encrypted" "MP-SPDZ")
PROJECT_ROOT="/home/lgp/MPCGuard"

for fw in "${FRAMEWORKS[@]}"; do
  echo "🚀 Running all YAML files in framework: $fw"

  cd "$PROJECT_ROOT/frameworks/$fw" || exit 1
  pwd
  rm -rf ./found_bugs_with_different_model

  CONFIG_DIR="./test_with_different_model_yaml/"

  for yaml_file in "$CONFIG_DIR"/*.yaml; do
    echo "▶️ Running config: $yaml_file in $fw"
    python ../../main.py --config="$yaml_file"
  done

  echo "✅ Finished $fw"
done
echo "🎉 Finsih all tests！"
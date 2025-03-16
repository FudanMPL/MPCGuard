#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <memory>
#include <set>
#include <algorithm>

using namespace std;

// 后缀树节点类
class SuffixTreeNode {
public:
    unordered_map<string, shared_ptr<SuffixTreeNode>> children;
    shared_ptr<SuffixTreeNode> suffixLink;
    int start;   // 边在序列中的起始索引
    int* end;    // 边在序列中的结束索引（指针以支持全局更新）
    int suffixIndex; // 叶子节点的后缀索引
    set<int> seqIds; // 序列ID集合
    unordered_map<int, vector<int>> positions; // 各序列中的起始位置列表

    SuffixTreeNode(int start, int* end) {
        this->start = start;
        this->end = end;
        suffixLink = nullptr;
        suffixIndex = -1;
    }

    int edgeLength() {
        return *end - start + 1;
    }
};

// SuffixTree 类
class SuffixTree {
public:
    vector<string> text; // 拼接后的序列
    vector<int> posToSeqId; // 每个位置对应的序列ID
    vector<int> posInSeq; // 每个位置在所属序列中的索引
    shared_ptr<SuffixTreeNode> root;

    SuffixTree(const vector<vector<string>>& sequences) {
        buildSuffixTree(sequences);
    }

    // 收集所有公共子串及其位置
    vector<pair<vector<string>, unordered_map<int, vector<int>>>> collectAllCommonSubstrings(int min_length) {
        vector<string> substr;
        vector<pair<vector<string>, unordered_map<int, vector<int>>>> result;
        collectDFS(root, substr, min_length, result);
        return result;
    }

private:
    shared_ptr<SuffixTreeNode> lastNewNode;
    shared_ptr<SuffixTreeNode> activeNode;

    int activeEdge;
    int activeLength;

    int remainingSuffixCount;
    int leafEnd;
    int* rootEnd;
    int* splitEnd;
    int size;

    unordered_map<int, string> seqEndSymbols; // 序列ID到分隔符的映射

    void buildSuffixTree(const vector<vector<string>>& sequences) {
        // 拼接所有序列，并添加唯一的分隔符，同时记录每个位置的序列ID和在序列中的位置
        int seqId = 0;
        int pos = 0;
        for (const auto& seq : sequences) {
            string endSymbol = "#" + to_string(seqId); // 唯一的分隔符
            seqEndSymbols[seqId] = endSymbol;
            int seqPos = 0;
            for (const auto& elem : seq) {
                text.push_back(elem);
                posToSeqId.push_back(seqId);
                posInSeq.push_back(seqPos);
                pos++;
                seqPos++;
            }
            text.push_back(endSymbol);
            posToSeqId.push_back(seqId);
            posInSeq.push_back(seqPos);
            pos++;
            seqId++;
        }

        size = text.size();
        rootEnd = new int(-1);
        root = make_shared<SuffixTreeNode>(-1, rootEnd);
        activeNode = root;

        activeEdge = -1;
        activeLength = 0;
        remainingSuffixCount = 0;
        leafEnd = -1;

        for (int i = 0; i < size; i++) {
            extendSuffixTree(i);
        }

        // 设置后缀索引和节点的 seqIds、positions
        int labelHeight = 0;
        setSeqIdsByDFS(root, labelHeight);
    }

    void extendSuffixTree(int pos) {
        leafEnd = pos;
        remainingSuffixCount++;
        lastNewNode = nullptr;

        while (remainingSuffixCount > 0) {
            if (activeLength == 0) {
                activeEdge = pos;
            }

            string currentEdge = text[activeEdge];

            if (activeNode->children.find(currentEdge) == activeNode->children.end()) {
                // 创建新叶子节点
                shared_ptr<SuffixTreeNode> leafNode = make_shared<SuffixTreeNode>(pos, &leafEnd);
                int seqId = posToSeqId[pos];
                leafNode->seqIds.insert(seqId);
                leafNode->positions[seqId].push_back(posInSeq[pos]);
                activeNode->children[currentEdge] = leafNode;

                // 更新后缀链接
                if (lastNewNode != nullptr) {
                    lastNewNode->suffixLink = activeNode;
                    lastNewNode = nullptr;
                }
            } else {
                shared_ptr<SuffixTreeNode> next = activeNode->children[currentEdge];
                if (walkDown(next)) {
                    continue;
                }

                if (text[next->start + activeLength] == text[pos]) {
                    // 已经在现有边上
                    if (lastNewNode != nullptr && activeNode != root) {
                        lastNewNode->suffixLink = activeNode;
                        lastNewNode = nullptr;
                    }
                    activeLength++;
                    break;
                }

                // 需要分裂边
                splitEnd = new int(next->start + activeLength - 1);
                shared_ptr<SuffixTreeNode> split = make_shared<SuffixTreeNode>(next->start, splitEnd);
                activeNode->children[currentEdge] = split;

                // 创建新叶子节点
                string leafEdge = text[pos];
                shared_ptr<SuffixTreeNode> leafNode = make_shared<SuffixTreeNode>(pos, &leafEnd);
                int seqId = posToSeqId[pos];
                leafNode->seqIds.insert(seqId);
                leafNode->positions[seqId].push_back(posInSeq[pos]);
                split->children[leafEdge] = leafNode;

                next->start += activeLength;
                split->children[text[next->start]] = next;

                // 更新后缀链接
                if (lastNewNode != nullptr) {
                    lastNewNode->suffixLink = split;
                }

                lastNewNode = split;
            }

            remainingSuffixCount--;

            if (activeNode == root && activeLength > 0) {
                activeLength--;
                activeEdge = pos - remainingSuffixCount + 1;
            } else if (activeNode != root) {
                activeNode = activeNode->suffixLink ? activeNode->suffixLink : root;
            }
        }
    }

    bool walkDown(shared_ptr<SuffixTreeNode> nextNode) {
        int edgeLen = nextNode->edgeLength();
        if (activeLength >= edgeLen) {
            activeEdge += edgeLen;
            activeLength -= edgeLen;
            activeNode = nextNode;
            return true;
        }
        return false;
    }

    void setSeqIdsByDFS(shared_ptr<SuffixTreeNode> node, int labelHeight) {
        if (node == nullptr) return;
        bool isLeaf = node->children.empty();

        if (isLeaf) {
            node->suffixIndex = size - labelHeight;
            // 叶子节点的 seqIds 和 positions 已经在创建时设置
            return;
        } else {
            for (auto& child : node->children) {
                setSeqIdsByDFS(child.second, labelHeight + child.second->edgeLength());
                // 内部节点的 seqIds 是所有子节点 seqIds 的并集
                node->seqIds.insert(child.second->seqIds.begin(), child.second->seqIds.end());
                // 内部节点的 positions 是所有子节点 positions 的合并
                for (const auto& kv : child.second->positions) {
                    node->positions[kv.first].insert(
                        node->positions[kv.first].end(),
                        kv.second.begin(),
                        kv.second.end()
                    );
                }
            }
        }
    }

    // 递归收集所有公共子串及其位置
    void collectDFS(shared_ptr<SuffixTreeNode> node, vector<string>& path, int min_length, vector<pair<vector<string>, unordered_map<int, vector<int>>>>& result) {
        if (node == nullptr) return;
        if (node->start != -1) {
            // 添加路径
            vector<string> edgeLabel;
            for (int i = node->start; i <= *(node->end); i++) {
                edgeLabel.push_back(text[i]);
            }
            path.insert(path.end(), edgeLabel.begin(), edgeLabel.end());
        }
        if (node->seqIds.size() == seqEndSymbols.size() && path.size() >= min_length) {
            // 收集公共子串及其位置
            result.emplace_back(path, node->positions);
        }
        for (auto& child : node->children) {
            collectDFS(child.second, path, min_length, result);
        }
        // 回溯路径
        if (node->start != -1) {
            int len = *(node->end) - node->start + 1;
            for (int i = 0; i < len; i++) {
                path.pop_back();
            }
        }
    }
};

// 处理覆盖关系，过滤子串
void filterSubstrings(vector<pair<vector<string>, unordered_map<int, vector<int>>>>& substrings, int numSeqs) {
    // 对于每个序列，记录每个位置被覆盖的最长子串长度
    vector<unordered_map<int, int>> seqPositionCoverage(numSeqs);

    // 按照子串长度从大到小排序
    sort(substrings.begin(), substrings.end(), [](const auto& a, const auto& b) {
        return a.first.size() > b.first.size();
    });

    vector<pair<vector<string>, unordered_map<int, vector<int>>>> filteredSubstrings;

    for (const auto& substrPair : substrings) {
        const auto& substr = substrPair.first;
        const auto& positions = substrPair.second;
        bool isCovered = false;
        for (int seqId = 0; seqId < numSeqs; ++seqId) {
            for (int pos : positions.at(seqId)) {
                // 检查当前位置是否已被更长的子串覆盖
                bool overlap = false;
                for (int i = pos; i < pos + substr.size(); ++i) {
                    if (seqPositionCoverage[seqId].count(i) && seqPositionCoverage[seqId][i] >= substr.size()) {
                        overlap = true;
                        break;
                    }
                }
                if (overlap) {
                    isCovered = true;
                    break;
                }
            }
            if (isCovered) break;
        }
        if (!isCovered) {
            // 子串未被覆盖，加入结果集
            filteredSubstrings.push_back(substrPair);
            // 更新覆盖信息
            for (int seqId = 0; seqId < numSeqs; ++seqId) {
                for (int pos : positions.at(seqId)) {
                    for (int i = pos; i < pos + substr.size(); ++i) {
                        seqPositionCoverage[seqId][i] = substr.size();
                    }
                }
            }
        }
    }

    substrings = filteredSubstrings;
}

int main() {
    // 序列列表
    vector<vector<string>> sequences = {
        {"1", "2", "3", "4", "6", "2", "3", "4", "5"},
        {"2", "3", "4", "6", "2", "3", "4"},
        {"0", "2", "3", "4", "6", "7"}
    };

    // 构建后缀树
    SuffixTree tree(sequences);

    // 收集所有公共子串，最小长度为 2
    vector<pair<vector<string>, unordered_map<int, vector<int>>>> substrings = tree.collectAllCommonSubstrings(2);

    // 过滤被覆盖的子串
    filterSubstrings(substrings, sequences.size());

    // 输出结果
    cout << "公共子串及其起始位置：" << endl;
    for (const auto& substrPair : substrings) {
        const auto& substr = substrPair.first;
        const auto& positions = substrPair.second;
        cout << "子串：";
        for (const auto& s : substr) {
            cout << s << " ";
        }
        cout << endl;
        cout << "位置：" << endl;
        for (int seqId = 0; seqId < sequences.size(); ++seqId) {
            cout << "  序列" << seqId << ": ";
            for (int pos : positions.at(seqId)) {
                cout << pos << " ";
            }
            cout << endl;
        }
    }

    return 0;
}

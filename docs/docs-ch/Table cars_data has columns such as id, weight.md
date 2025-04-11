Table cars_data has columns such as id, weight.\nid is the primary key.\nTable model_list has columns such as maker, model.

Table model_list has columns such as model, maker.\nTable cars_data has columns such as id, weight.\nid is the primary key.

python evaluation.py --gold /Users/jizha/code/python/spider/dataset/spider/dev_gold.sql  --pred /Users/jizha/code/python/test-suite-sql-eval/二轮测试_gpt4_choice.json --etype all --db  /Users/jizha/code/python/spider/dataset/spider/database  --table tables.json

```sh
python generate_question.py \
--data_type spider \
--split test \
--tokenizer gpt-3.5-turbo \
--max_seq_len 4096 \
--selector_type EUCDISMASKPRESKLSIMTHR \
--pre_test_result /Users/jizha/code/python/test-suite-sql-eval/随机列测试/union_test_20231201_random_table.sql \
--prompt_repr SQL \
--k_shot 9 \
--example_type QA

```

```
import argparse
import os
import json

import openai
from tqdm import tqdm

from llm.chatgpt import init_chatgpt, ask_llm
from utils.enums import LLM
from torch.utils.data import DataLoader

from utils.post_process import process_duplication, get_sqls
import concurrent.futures

QUESTION_FILE = "questions.json"


def gen_predict_sql(index, token_cnt, args, batch):
    try:
        res = ask_llm(args.model, batch, args.temperature, args.n)
    except openai.error.InvalidRequestError:
        print(f"The {i}-th question has too much tokens! Return \"SELECT\" instead")
        res = ""
    # parse result
    token_cnt += res["total_tokens"]
    results = []
    if args.n == 1:
        for sql in res["response"]:
            # remove \n and extra spaces
            sql = " ".join(sql.replace("\n", " ").split())
            sql = process_duplication(sql)
            # python version should >= 3.8
            if sql.startswith("SELECT"):
                results.append(sql)
            elif sql.startswith(" "):
                results.append("SELECT" + sql)
            else:
                results.append("SELECT " + sql)
    else:
        cur_db_ids = db_ids[i * args.batch_size: i * args.batch_size + len(batch)]
        for sqls, db_id in zip(res["response"], cur_db_ids):
            processed_sqls = []
            for sql in sqls:
                sql = " ".join(sql.replace("\n", " ").split())
                sql = process_duplication(sql)
                if sql.startswith("SELECT"):
                    pass
                elif sql.startswith(" "):
                    sql = "SELECT" + sql
                else:
                    sql = "SELECT " + sql
                processed_sqls.append(sql)
            result = {
                'db_id': db_id,
                'p_sqls': processed_sqls
            }
            final_sqls = get_sqls([result], args.n, args.db_dir)
            results = final_sqls
    return index, results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", type=str)
    parser.add_argument("--openai_api_key", type=str, default="eab38a33cc07467aae9b7d09783b75a8")
    parser.add_argument("--openai_group_id", type=str, default="luli.wjc")
    parser.add_argument("--openai_api_base", type=str,
                        default="https://codegencore.antgroup-inc.cn/api/chat/commonPower/v1")
    parser.add_argument("--model", type=str, choices=[LLM.TEXT_DAVINCI_003,
                                                      LLM.GPT_35_TURBO,
                                                      LLM.GPT_35_TURBO_0613,
                                                      LLM.TONG_YI_QIAN_WEN,
                                                      LLM.GPT_35_TURBO_16K,
                                                      LLM.GPT_4],
                        default=LLM.GPT_35_TURBO)
    parser.add_argument("--start_index", type=int, default=0)
    parser.add_argument("--end_index", type=int, default=1000000)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--mini_index_path", type=str, default="")
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--n", type=int, default=1, help="Size of self-consistent set")
    parser.add_argument("--db_dir", type=str, default="dataset/spider/database")
    args = parser.parse_args()

    # check args
    assert args.model in LLM.BATCH_FORWARD or \
           args.model not in LLM.BATCH_FORWARD and args.batch_size == 1, \
        f"{args.model} doesn't support batch_size > 1"

    questions_json = json.load(open(os.path.join(args.question, QUESTION_FILE), "r"))
    questions = [_["prompt"] for _ in questions_json["questions"]]
    db_ids = [_["db_id"] for _ in questions_json["questions"]]

    # init openai api
    init_chatgpt(args.openai_api_key, args.openai_group_id, args.openai_api_base, args.model)

    if args.start_index == 0:
        mode = "w"
    else:
        mode = "a"

    if args.mini_index_path:
        mini_index = json.load(open(args.mini_index_path, 'r'))
        questions = [questions[i] for i in mini_index]
        out_file = f"{args.question}/RESULTS_MODEL-{args.model}_MINI.txt"
    else:
        out_file = f"{args.question}/RESULTS_MODEL-{args.model}.txt"

    question_loader = DataLoader(questions, batch_size=args.batch_size, shuffle=False, drop_last=False)

    token_cnt = 0
    results = []
    with open(out_file, mode) as f:
        for i in tqdm(range(0, len(question_loader), 10)):
            up = i + 10
            if len(question_loader) < up:
                up = len(question_loader)
            result_temp = [""] * (up - i)
            future_list = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                question_batch = question_loader[i:up]
                for index, item in enumerate(question_batch):
                    future_list.append(executor.submit(gen_predict_sql, index, token_cnt, args, item))
                for future in concurrent.futures.as_completed(future_list):
                    index, p_sqls = future.result()
                    result_temp[index] = p_sqls
            for item in result_temp:
                f.write("".join(item))
                results.extend(item)


```


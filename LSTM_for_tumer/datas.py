import sys, pickle, os, random
import numpy as np


tag2label = {"O": 0, "B-TU": 1, "I-TU": 2}


def read_testdata(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = ''
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    for line in lines:
        if line != '\n':
            data += line 
    return data


def output_data(TUMER, corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    f = open(corpus_path, 'a', encoding = 'UTF-8')
    f.write(TUMER)
    f.write('\n')



def read_corpus(corpus_path):
    """
    read corpus and return the list of samples
    :param corpus_path:
    :return: data
    """
    data = []
    i = 0
    with open(corpus_path, encoding='utf-8') as fr:
        lines = fr.readlines()
    sent_, tag_ = [], []
    for line in lines:
        if line != '\n':
            i = i+1
            # print (line + str(i))
            [char, label] = line.strip().split()
            #print(char + ':' +label)
            sent_.append(char)
            if label == 'I':
                print(line)
            tag_.append(label)
        else:
            data.append((sent_, tag_))
            sent_, tag_ = [], []
#    print('length:' + str(len(data)))
    return data


def vocab_build(vocab_path, corpus_path, min_count):
    """

    :param vocab_path:
    :param corpus_path:
    :param min_count:
    :return:
    """
    data = read_corpus(corpus_path)
    word2id = {}
    for sent_, tag_ in data:
        for word in sent_:
            if word.isdigit():
                word = '<NUM>'
            elif ('\u0041' <= word <='\u005a') or ('\u0061' <= word <='\u007a'):
                word = '<ENG>'
            if word not in word2id:
                word2id[word] = [len(word2id)+1, 1]
            else:
                word2id[word][1] += 1
    low_freq_words = []
    for word, [word_id, word_freq] in word2id.items():
        if word_freq < min_count and word != '<NUM>' and word != '<ENG>':
            low_freq_words.append(word)
    for word in low_freq_words:
        del word2id[word]

    new_id = 1
    for word in word2id.keys():
        word2id[word] = new_id
        new_id += 1
    word2id['<UNK>'] = new_id
    word2id['<PAD>'] = 0

#    print(len(word2id))
    with open(vocab_path, 'wb') as fw:
        pickle.dump(word2id, fw)


def sentence2id(sent, word2id):
    """

    :param sent:
    :param word2id:
    :return:
    """
    sentence_id = []
    for word in sent:

        #pretrained character embedding不使用以下两行代码
        # if word.isdigit():
        #     word = '<NUM>'
        # elif ('\u0041' <= word <= '\u005a') or ('\u0061' <= word <= '\u007a'):
        #     word = '<ENG>'
        if word not in word2id:
            word = '<UNK>'
        sentence_id.append(word2id[word])
    return sentence_id


def read_dictionary_random(vocab_path):
    """

    :param vocab_path:
    :return:
    """
    vocab_path = os.path.join(vocab_path)
    with open(vocab_path, 'rb') as fr:
        word2id = pickle.load(fr)
    return word2id

def read_dictionary_pretrain(vocab_path):
    """
    获取一个dictionary，其中key是汉字，value是汉字在字典中的位置顺序
    """
    char_dict = {}
    with open(vocab_path,'r',encoding='utf-8') as fr:
        lines = fr.readlines()
        index = 1
        char_dict['<PAD>'] = 0

        for l in lines:
            char_dict[l.strip()] = index
            index += 1
        char_dict['<UNK>'] = index
    fr.close
    return char_dict

def random_embedding(vocab, embedding_dim):
    """

    :param vocab:
    :param embedding_dim:
    :return:
    """
    embedding_mat = np.random.uniform(-0.25, 0.25, (len(vocab), embedding_dim))
    embedding_mat = np.float32(embedding_mat)
    return embedding_mat

def get_pretrained_embedding(embedding_path, embedding_dim):
    """
    pre-trained character_embedding，其格式为ndarray,维度为vocab.size * embedding_dim
    """
    embedding_pad = np.random.uniform(-1, 1, (1, embedding_dim))
    embedding_pad = np.float32(embedding_pad)
    embedding_unk = np.random.uniform(-1, 1, (1, embedding_dim))
    embedding_unk = np.float32(embedding_unk)
    embedding_pretrain = np.loadtxt(embedding_path)
    embedding_mat = np.concatenate((embedding_pad, embedding_pretrain), axis=0)
    embedding_mat = np.concatenate((embedding_mat, embedding_unk), axis=0)
    embedding_mat = np.float32(embedding_mat)
    print(embedding_mat.shape)
    return embedding_mat

def pad_sequences(sequences, pad_mark=0):
    """

    :param sequences:
    :param pad_mark:
    :return:
    """
    max_len = max(map(lambda x : len(x), sequences))
    seq_list, seq_len_list = [], []
    for seq in sequences:
        seq = list(seq)
        seq_ = seq[:max_len] + [pad_mark] * max(max_len - len(seq), 0)
        seq_list.append(seq_)
        seq_len_list.append(min(len(seq), max_len))
    return seq_list, seq_len_list


def batch_yield(data, batch_size, vocab, tag2label, shuffle=False):
    """

    :param data:
    :param batch_size:
    :param vocab:
    :param tag2label:
    :param shuffle:
    :return:
    """
    if shuffle:
        random.shuffle(data)

    seqs, labels = [], []
    for (sent_, tag_) in data:
        sent_ = sentence2id(sent_, vocab)
        label_ = [tag2label[tag] for tag in tag_]

        if len(seqs) == batch_size:
            yield seqs, labels
            seqs, labels = [], []

        seqs.append(sent_)
        labels.append(label_)

    if len(seqs) != 0:
        yield seqs, labels


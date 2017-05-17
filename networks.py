__author__ = 'Alexandros Armaos  (alexandros@tartaglialab.com )'
import lasagne
from lasagne import *
from lasagne.layers import Layer
import DCNN
import theano.tensor as T


def parseActivation(str_a):
    if str_a=="linear":
        return lasagne.nonlinearities.linear
    elif str_a=="tanh":
        return lasagne.nonlinearities.tanh
    elif str_a=="rectify":
        return lasagne.nonlinearities.rectify
    elif str_a=="sigmoid":
        return lasagne.nonlinearities.sigmoid
    else:
        raise Exception("Activation function \'"+str_a+"\' is not recognized")


def buildDCNNPaper(batch_size,vocab_size,embeddings_size=48,filter_sizes=[10,7],nr_of_filters=[6,12],activations=["tanh","tanh"],ktop=5,dropout=0.5,output_classes=2,padding='last'):

    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, None),
    )

    l_embedding = DCNN.embeddings.SentenceEmbeddingLayer(
        l_in,
        vocab_size,
        embeddings_size,
        padding=padding
    )


    l_conv1 = DCNN.convolutions.Conv1DLayerSplitted(
        l_embedding,
        nr_of_filters[0],
        filter_sizes[0],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )

    l_fold1 = DCNN.folding.FoldingLayer(l_conv1)

    l_pool1 = DCNN.pooling.DynamicKMaxPoolLayer(l_fold1,ktop,nroflayers=2,layernr=1)


    l_nonlinear1 = lasagne.layers.NonlinearityLayer(l_pool1,nonlinearity=parseActivation(activations[0]))

    l_conv2 = DCNN.convolutions.Conv1DLayerSplitted(
        l_nonlinear1,
        nr_of_filters[1],
        filter_sizes[1],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )

    l_fold2 = DCNN.folding.FoldingLayer(l_conv2)

    l_pool2 = DCNN.pooling.KMaxPoolLayer(l_fold2,ktop)

    l_nonlinear2 = lasagne.layers.NonlinearityLayer(l_pool2,nonlinearity=parseActivation(activations[1]))

    l_dropout2=lasagne.layers.DropoutLayer(l_nonlinear2,p=dropout)

    l_out = lasagne.layers.DenseLayer(
        l_dropout2,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax
        )

    return l_out

def build1DDCNN(batch_size,channels_size,vocab_size,filter_sizes=[20,7],nr_of_filters=[6,12],activations=["tanh","tanh"],ktop=5,dropout=0.5,output_classes=2,padding='last'):
# 2 conv layers , explicity! after there is the dynamic version of the same where you create as much conv layers as you want
    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, channels_size, 1, None),
    )

    l_conv1 = DCNN.convolutions.Conv1DLayer(
        l_in,
        nr_of_filters[0],
        filter_sizes[0],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )

    l_pool1 = DCNN.pooling.DynamicKMaxPoolLayer(l_conv1,ktop,nroflayers=2,layernr=1)


    l_nonlinear1 = lasagne.layers.NonlinearityLayer(l_pool1,nonlinearity=parseActivation(activations[0]))

    l_conv2 = DCNN.convolutions.Conv1DLayer(
        l_nonlinear1,
        nr_of_filters[1],
        filter_sizes[1],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )


    l_pool2 = DCNN.pooling.KMaxPoolLayer(l_conv2,ktop)

    l_nonlinear2 = lasagne.layers.NonlinearityLayer(l_pool2,nonlinearity=parseActivation(activations[1]))

    l_dropout2=lasagne.layers.DropoutLayer(l_nonlinear2,p=dropout)

    l_out = lasagne.layers.DenseLayer(
        l_dropout2,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax
        )

    return l_out

def build1DDCNN_dynamic(nlayers,batch_size,channels_size,vocab_size,filter_sizes=[20,7],nr_of_filters=[6,12],activations=["tanh","tanh"],ktop=5,dropout=0.5,output_classes=2,padding='last'):
# 1dddcnn where even the number of layers is dynamic here
    layers=[]

    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, channels_size, 1, None),
    )

    layers.append(l_in)

    for l in range(0, nlayers):
        l_conv = DCNN.convolutions.Conv1DLayer(
            layers[-1],
            nr_of_filters[l],
            filter_sizes[l],
            nonlinearity=lasagne.nonlinearities.linear,
            border_mode="full"
        )
        layers.append(l_conv)

        if l<nlayers-1:
            l_pool = DCNN.pooling.DynamicKMaxPoolLayer(layers[-1],ktop,nroflayers=nlayers,layernr=l+1)
        if l==nlayers-1:
            l_pool = DCNN.pooling.KMaxPoolLayer(layers[-1],ktop)
        layers.append(l_pool)

        l_nonlinear = lasagne.layers.NonlinearityLayer(layers[-1],nonlinearity=parseActivation(activations[l]))



    l_dropout=lasagne.layers.DropoutLayer(layers[-1],p=dropout)

    l_out = lasagne.layers.DenseLayer(
        l_dropout,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax
        )

    return l_out

def build1DCNN_dynamic(nlayers,batch_size,filter_sizes=[20,7],nr_of_filters=[6,12],activations=["tanh","tanh"],dropout=0.5,output_classes=2,padding='last'):
# even the number of layers is dynamic here
    layers=[]

    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, 1, 3, 100),
    )

    layers.append(l_in)

    for l in range(0, nlayers):
        l_conv = DCNN.convolutions.Conv1DLayerSplittedSameFilter(
            layers[-1],
            nr_of_filters[l],
            filter_sizes[l],
            nonlinearity=lasagne.nonlinearities.linear,
            border_mode="full"
        )
        layers.append(l_conv)

        '''l_fold = DCNN.folding.FoldingLayer(layers[-1])
        layers.append(l_fold)'''

        #l_pool = lasagne.layers.pool.MaxPool1DLayer(layers[-1],pool_size=3)

        l_pool = DCNN.pooling.PoolPerLine(layers[-1],pool_size=2)
        layers.append(l_pool)


        l_nonlinear = lasagne.layers.NonlinearityLayer(layers[-1],nonlinearity=parseActivation(activations[l]))



    l_dropout=lasagne.layers.DropoutLayer(layers[-1],p=dropout)


    l_out = lasagne.layers.DenseLayer(
        l_dropout,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax
        )

    return l_out


def build2DDCNN(batch_size,vocab_size,embeddings_size=48,filter_sizes=[10,7],nr_of_filters=[24,12],activations=["tanh","tanh"],ktop=5,dropout=0.5,output_classes=2,padding='last'):

    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, None),
    )


    l_conv1 = DCNN.convolutions.Conv2DLayer(
        l_in,
        nr_of_filters[0],
        filter_sizes[0],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )

    l_pool1 = DCNN.pooling.DynamicKAreasMaxPoolLayer(l_conv1,ktop,nroflayers=2,layernr=1)


    l_nonlinear1 = lasagne.layers.NonlinearityLayer(l_pool1,nonlinearity=parseActivation(activations[0]))

    l_conv2 = DCNN.convolutions.Conv2DLayer(
        l_nonlinear1,
        nr_of_filters[1],
        filter_sizes[1],
        nonlinearity=lasagne.nonlinearities.linear,
        border_mode="full"
    )

    l_fold2 = DCNN.folding.FoldingLayer(l_conv2)

    l_pool2 = DCNN.pooling.KMaxPoolLayer(l_fold2,ktop)

    l_nonlinear2 = lasagne.layers.NonlinearityLayer(l_pool2,nonlinearity=parseActivation(activations[1]))

    l_dropout2=lasagne.layers.DropoutLayer(l_nonlinear2,p=dropout)

    l_out = lasagne.layers.DenseLayer(
        l_dropout2,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax
        )

    return l_out




def buildMaxTDNN(batch_size,vocab_size,embeddings_size,filter_size,output_classes):

    l_in = lasagne.layers.InputLayer(
        shape=(batch_size, None),
    )

    l_embedding = DCNN.embeddings.SentenceEmbeddingLayer(l_in, vocab_size, embeddings_size)


    l_conv1 = DCNN.convolutions.Conv1DLayer(
        l_embedding,
        1,
        filter_size,
        nonlinearity=lasagne.nonlinearities.tanh,
        stride=1,
        border_mode="valid",

    )

    l_pool1 = lasagne.layers.GlobalPoolLayer(l_conv1,pool_function=T.max)

    l_out = lasagne.layers.DenseLayer(
        l_pool1,
        num_units=output_classes,
        nonlinearity=lasagne.nonlinearities.softmax,
        )

    return l_out

# This isn't real python, but an interpreted language,
# that a compiler script, yet to be built,
# will convert to the Commands data structure of the BB API
# and will be inserted into the BB application via
# automated API calls

L is for local command
R is for remote command
internal commands are like such: connect()
R and L return data in file form
RV and LV return data in variable form
you can append to file like such: a += R("b")

def cdDBL():
    L("cd %%DBL%%")


def loop_through_file(file,function,step = 1):
    count = LV("cat %file% | wc -l")
    block = LV("head -%step% %file% | sed -i '%step%d' %file%")
    while_var(count,">0",function,step,block)


def while_var(var,condition,function,decrement,args):
    if_var(var,condition):
        function(args)
        var = V(var - decrement)
        while_var(var,condition,function,decrement)


def check_for_vlan(name):
    interface.txt = R("show interface %name%")
    interface = LV("cat interface.txt | grep 'Vlan'")
    if_var(interface,"notEmpty"):
        results += L("echo %interface%")


success_result = {
    command: echo 'good'
    status: success,
    text: 'good',
    save: None
}

fail_result = {
    command: echo 'bad %res%'
    status: fail,
    text: 'bad',
    save: None
}


main():
    Connect()
    cdDBL()
    version.txt = R("show version")
    ints.txt = R("show interfaces")

    # get interfaces names, they appear on NON indented lines
    intNames.txt = L('cat ints.txt | grep -E "^[^ ]"')

    # search for interfaces with vlan
    loop_through_file(intNames.txt,check_for_vlan)
    res = LV("cat results")

    if_var(res,"notEmpty and notContains 'No such'"):
        return(success_result)

    else:
        return(fail_result)
    # which is equal to
    if_var(res,"isEmpty or contains 'No such'"):
        return(fail_result)

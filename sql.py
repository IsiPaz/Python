import re
import os

#Columna tanto con punto como sin punto y espacio entre nombres
columna = '([A-Za-z][A-Za-z0-9_]*|[A-Za-z][A-Za-z0-9_]*\.[A-Za-z][A-Za-z0-9_]*)'
er_columna = re.compile(columna)

#Valores
valores = r'(\'([A-Za-z0-9_ -])+\'|[0-9]+|[0-9]\.[0-9])'
er_valores = re.compile(valores)

#Nombre para las tablas (suponinedo que estan formadas por solo una palabra)
nombre_tabla = '[A-Za-z][A-Za-z0-9_]*'

## INSERT ##
#" INSERT INTO " tabla "(" columna {" ," columna2 }")" " VALUES (" valor {" ," valor2 }");"

columnas = '(\([ ]*'+columna+'[ ]*\)[ ]*| \([ ]*'+columna+'[ ]*([ ]*,[ ]*'+columna+'[ ]*)*\)[ ]*)'
varios_valores = '([ ]*\([ ]*'+valores+'[ ]*\)[ ]*|[ ]*\([ ]*'+valores+'[ ]*([ ]*,[ ]*'+valores+'[ ]*)*\))'
insert_basic = '[ ]*INSERT INTO[ ]+'+nombre_tabla+'[ ]*'+columnas+'[ ]+VALUES[ ]+'+varios_valores+'[ ]*;'

er_insert = re.compile(insert_basic)


valores_sin_cosas = '([ ]*\([ ]*'+valores+'[ ]*|[ ]*\([ ]*'+valores+'[ ]*\)[ ]*;*|[ ]*'+valores+'[ ]*|[ ]*'+valores+'[ ]*\)[ ]*;*)'
er_valores_sin_cosas = re.compile(valores_sin_cosas)

columnas_sin_coma = '(\([ ]*'+columna+'[ ]*,*|,?'+columna+'[ ]*|[ ]*'+columna+',?|,?'+columna+'[ ]*\)|[ ]*\([ ]*'+columna+'[ ]*\)[ ]*)' ##quiza falta agregar [ ]*\([ ]*'+columna+'[ ]*\)[ ]*
er_columna_sin_coma = re.compile(columnas_sin_coma)


## UPDATE ##
#" UPDATE " tabla "SET" columna "=" valor {" ," columna "=" valor } " WHERE " columna "=" valor {(" AND" columna "=" valor |" OR" columna "=" valor )}";"

set_basic = r'[ ]+SET[ ]+('+columna+r'[ ]*=[ ]*'+valores+')'
set_con_muchas_igualdades = set_basic+r'((([ ]*,[ ]*'+columna+r'[ ]*=[ ]*'+valores+'))+)?'
where_basic_u = r'[ ]+WHERE[ ]+('+columna+r'[ ]*=[ ]*'+valores+')'
where_plus_and_or_u = where_basic_u +r'(([ ]+AND[ ]+('+columna+r'[ ]*=[ ]*'+valores+'))|([ ]+OR[ ]+('+columna+r'[ ]*=[ ]*'+valores+'))+)?'
update_basic = r'[ ]*UPDATE[ ]+'+nombre_tabla+'[ ]*'
update_all = update_basic+set_con_muchas_igualdades+where_plus_and_or_u+r'[ ]*;'

er_update = re.compile(update_all)

## SELECT ##
#" SELECT " ( columna {" ," columna } | "*") " FROM " tabla
#[" INNER JOIN " tabla ]
#[" WHERE " ( columna "=" valor | columna "=" columna ) {(" AND "|" OR ") ( columna "=" valor | columna "=" columna )}]
#[" ORDER BY" columna (" ASC "|" DESC ")]

#WHERE BASIC
where_basic = r'[ ]+WHERE[ ]+(('+columna+r'[ ]*=[ ]*'+valores+')|('+columna+r'[ ]*=[ ]*'+columna+r'))'

#SELECT
select_basic = r'[ ]*SELECT[ ]+(('+columna+r'([ ]*,[ ]*'+columna+r')*)|\*)[ ]+FROM[ ]+'+nombre_tabla+r'[ ]*'
where_plus_and_or = where_basic + r'(([ ]+(AND|OR)[ ]+(('+columna+r'[ ]*=[ ]*'+valores+')|('+columna+r'[ ]*=[ ]*'+columna+r')))+)?'
select_con_where = select_basic + r'(' + where_plus_and_or + r')?[ ]*;'
inner_join_basic = r'[ ]+INNER JOIN[ ]+'+nombre_tabla+r'[ ]*'+where_plus_and_or+r''
select_con_inner = select_basic + r'(' + inner_join_basic + r')?[ ]*;'
order_by = r'[ ]+ORDER BY[ ]+'+columna+r'[ ]+(ASC|DESC)'
select_con_order_by = select_basic+ r'(' + order_by + r')?[ ]*;'
select_con_inner_order_by = select_basic+inner_join_basic+order_by+r'[ ]*;'
select_con_where_order_by = select_basic+where_plus_and_or+order_by+r'[ ]*;'

select = r'(('+select_con_inner+r'|'+select_con_where+r'|'+select_con_order_by+r'|'+select_con_inner_order_by+r'|'+select_con_where_order_by+r')?)'


er_select = re.compile(select)

#######################################################################
#FUNCIONES
#######################################################################

#Nombre: revisar_sintaxis:

#Entrada: comando de tipo string, la instruccion dada por el usuario.
#Salida:entero, 1 si el comando tiene la sintaxis correcta o -1 si tiene la sintaxis incorrecta.

#Descripcion: revisa si la sintaxis del comando es correcta segun las expresiones regulares dadas mas arriba.

def revisar_sintaxis(comando):

    caso = re.split('[ ]',comando) ##ME RETORNA UNA LISTA DE SOLO PALABRAS :D, no toma en cuenta los espacios

    if(caso[0]=='SELECT'):
        a = er_select.fullmatch(comando)
        if a == None:
            return -1
        else:
            return 1

    elif(caso[0]=='UPDATE'):
        c = er_update.fullmatch(comando)
        if c == None:
            return -1
        else:
            return 1

    elif(caso[0]=='INSERT' and caso[1]=='INTO'):
        j = er_insert.fullmatch(comando)
        if j == None:
            return -1
        else:
            return 1
    else :
        return -1
####################################################################
#Nombre: guardar_tabla

#Entrada: recibe el nombre de la tabla y un diccionario que contiene tablas.
#Salida: no retorna nada.

#Descripcion: funcion que crea una lista de listas de la tabla que se desea trabajar y se guarda en un diccionario.
def guardar_tabla(nombre_t,dic_de_tablas) :

    if not os.path.exists(nombre_t+'.csv'):
        return print('el archivo no existe')
    else:
        arch = open(nombre_t+'.csv','r')
        lista_tabla = []

        for linea in arch :
            lista_tabla.append(linea.strip(' ').strip().split(','))

        dic_de_tablas[nombre_t]=lista_tabla

        arch.close()
####################################################################
#Nombre: actualizar_archivo

#Entrada: recibe el nombre de la tabla y una lista de listas de la tabla que se desea updatear
#Salida: no retorna nada

#Descripcion: funcion que reescribe un archivo con la tabla luego de ser updateada
def actualizar_archivo(nombre_tabla,tabla_update):
    arch = open(nombre_tabla+'.csv','w')

    for fila in tabla_update:
        comas=len(fila)-1
        for palabra in fila:
            arch.write(palabra)
            if comas!=0:
                arch.write(',')
                comas=comas-1
        arch.write("\n")
    arch.close()
#######################################################################
#Nombre: Insert

#Entrada: instruccion de tipo string, dada por el usuario
#Salida: retorna una confirmacion de la insercion de alguna filas

#Descripcion: Inserta una nueva fila al final del archivo
def insert(inst):

    p1_p2 = re.split('VALUES',inst) #SEPARA LA EXPRESION JUSTO EN VALUES
    p1 = p1_p2[0]
    c = re.split('[ ]+',p1)
    p2 = p1_p2[1]
    c1 = re.split('[ ]*,[ ]*',p2)

    nombre_tabla = c[2]


    i=3
    columnas = []
    valores = []

    while i<len(c):

        x=c[i]
        if (er_columna_sin_coma.fullmatch(x) != None):
            columnas.append(x)
            i+=1
        else :
            i+=1
    columnas_finales = []

    for z in columnas:
        w = z.strip('(').strip(')').strip(',')
        columnas_finales.append(w)


    i=0
    while i<len(c1):

        x=c1[i]
        if (er_valores_sin_cosas.fullmatch(x) != None):
            valores.append(x)
            i+=1
        else :
            i+=1

    valores_finales = []

    for z in valores:
        w = z.strip('[ ]*\([ ]*').strip('[ ]*\)[ ]*;*').strip('[ ]*')
        valores_finales.append(w.strip("[ ]*\'[ ]*"))

    ## HASTA AQUI TENGO EL NOMBRE DE LA TABLA, LAS COLUMNAS Y VALORES
    if (len(columnas_finales)!=len(valores_finales)): ##comprobacion de que se entregan la misma cantidad de columnas y valores
        return print("Nombre de Sintaxis !")

    if not os.path.exists(nombre_tabla+'.csv'):
        print('el archivo no existe')
    else :
        archivo = open(nombre_tabla+'.csv','r')
        primera_linea = []
        i=0

        while i<1:
            line = archivo.readline()
            i+=1

        primera_linea=line.strip().split(',')
        linea_para_insertar = []
        largo = len(primera_linea)
        i = 0
        v= " "
        while i<largo :
            linea_para_insertar.append(v)
            i+=1

        for x in range(len(valores_finales)):
            ind=primera_linea.index(columnas_finales[x])
            linea_para_insertar[ind]=valores_finales[x]

        l_f = ','.join(linea_para_insertar)
        archivo.close()
        archivo = open(nombre_tabla+'.csv','a')
        archivo.write("\n")
        archivo.write(l_f)
        print("Se ha insertado 1 fila")
        archivo.close()
#######################################################################
#Nombre: Update

#Entrada: instruccion de tipo string, dada por el usuario
#Salida: retorna una confirmacion de la insercion de alguna filas

#Descripcion: Inserta una nueva fila al final del archivo
def update(inst):

    dic_de_tablas={}

    lista_indices_columnas_where=[] ##AQUI VAN LOS INDICES DE CADA COLUMNA DEL WHERE
    where_valores=[]

    lista_indice_set=[] ##indices de las columans set
    lista_set_valores=[]

    columnas_finales=[]
    columnas_f1=[]
    where_c_v = [] #lista de las columnas y valores donde se guardara, pares-->columnas, impares-->valores
    p1_p2=re.split('WHERE',inst)
    p1=p1_p2[0]

    sin_set=re.split('SET',p1)
    columnas = sin_set[1]
    columnas_f = re.split('[ ]*,[ ]*',columnas)
    c=re.split('[ ]+',p1)

    p2=p1_p2[1]
    c1=re.split('[ ]*,[ ]*',p2)
    nombre_tabla=c[1]


    columnas_where=[]
    for i in c1:
        x=re.split('[ ]*=[ ]*',i)
        for y in x:
            columnas_where.append(y.strip(' ').strip(';'))#Columnas del where, par son columnas, impar son valores


    guardar_tabla(nombre_tabla,dic_de_tablas)

    tabla_update = dic_de_tablas[nombre_tabla]
    primera_fila=tabla_update[0]

    for x in columnas_f:
        j=re.split('[ ]*=[ ]*',x)
        for j1 in j:
            columnas_f1.append(j1.strip(' ')) ##ESTAS SON LAS COSAS QUE GUARDAREMOS, SIEMPRE LOS PARES SON COLUMNAS Y LOS IMPARES VALORES

    if ('AND' in inst and 'OR' in inst):

        lista_where_and=[]
        lista_where_sin_and=[]


        x=re.split('[ ]*OR[ ]*',p2)
        for y in x:
            if 'AND' in y:
                x1=re.split('[ ]*AND[ ]*',y)
                for i in x1:
                    lista_where_and.append(i.strip(' ').strip(';'))#los pares son columnas, los impares son valores
            else:
                lista_where_sin_and.append(y.strip(' ').strip(';'))



        #recorrer lista sin and:

        if lista_where_sin_and!=[]:
            for where in lista_where_sin_and:
                columnas_where=re.split('[ ]*=[ ]*',where)

                lista_indice_de_columnas=[]
                lista_indice_de_valores=[]

                i=0
                while i<len(columnas_where):  #verifica si existe la columna del where:
                    if i%2==0:
                        if (columnas_where[i] in primera_fila):
                            lista_indice_de_columnas.append(primera_fila.index(columnas_where[i]))
                            i+=1
                        else:
                            return print("no existe la columna")
                    i+=1

                i=0
                j=0

                while i<len(columnas_where):
                    pos=lista_indice_de_columnas[0]
                    if i%2==1:
                        for j in tabla_update:
                            if columnas_where[i]==j[pos]:
                                lista_indice_de_valores.append(tabla_update.index(j))
                            else:
                                continue
                        i+=1
                    else:
                        i+=1

                i=0
                while i<len(columnas_f1):
                    if i%2==0:
                        if (columnas_f1[i] in primera_fila):
                            lista_indice_set.append(primera_fila.index(columnas_f1[i]))
                            i+=1
                        else:
                            return print("no existe la columna")
                            i+=1
                    else:
                        i+=1

                j=0
                i=0
                l=0

                while j<len(tabla_update):
                    if j in lista_indice_de_valores:
                        for k in lista_indice_set:

                            while l<len(columnas_f1):
                                if l%2==1:
                                    tabla_update[j][k]=columnas_f1[l]

                                    l+=1
                                    i+=1
                                    break
                                else:
                                    l+=1
                        j+=1
                    else:
                        j+=1


                print('Se ha actualizado ',i,' filas')

        #recorre la lista con and:

        if lista_where_and!=[]:

            lista_where1=[]
            CONTADOR=0 #PONER EL MODULO 2
            lista_indice_de_valores=[]
            for where in lista_where_and:
                columnas_where=re.split('[ ]*=[ ]*',where)
                lista_indice_de_columnas=[]
                lista_indice_set=[]



                i=0
                while i<len(columnas_where):  #verifica si existe la columna del where:
                    if i%2==0:
                        if (columnas_where[i] in primera_fila):
                            lista_indice_de_columnas.append(primera_fila.index(columnas_where[i]))
                            i+=1
                        else:
                            return print("no existe la columna")


                    i+=1

                i=0
                j=0

                while i<len(columnas_where):
                    pos=lista_indice_de_columnas[0]
                    if i%2==1:
                        for j in tabla_update:
                            if columnas_where[i]==j[pos]:

                                lista_indice_de_valores.append(tabla_update.index(j))

                            else:
                                continue
                        i+=1
                    else:
                        i+=1


                i=0

                while i<len(columnas_f1):
                    if i%2==0:
                        if (columnas_f1[i] in primera_fila):
                            lista_indice_set.append(primera_fila.index(columnas_f1[i]))
                            i+=1
                        else:
                            return print("no existe la columna")
                            i+=1
                    else:
                        i+=1


                CONTADOR+=1

            j=0
            i=0
            l=0

            a=lista_indice_de_valores[len(lista_indice_de_valores)-1]
            lista_indice_de_valores.append(a)
            if CONTADOR!=(len(lista_where_and)):
                return print('Se han actualizado 0 filas')

            else:

                m=0
                while m<len(lista_indice_de_valores):
                    n=lista_indice_de_valores[0]
                    lista_indice_de_valores.remove(lista_indice_de_valores[0])
                    if n in lista_indice_de_valores:
                        l=0
                        j=0
                        while j<len(tabla_update):
                            if j in lista_indice_de_valores:
                                for k in lista_indice_set:
                                    while l<len(columnas_f1):
                                        if l%2==1:
                                            tabla_update[j][k]=columnas_f1[l]
                                            l+=1
                                            i+=1

                                        else:
                                            l+=1
                                break
                                j+=1
                            else:
                                j+=1




                print('Se ha actualizado ',i,' filas')
            actualizar_archivo(nombre_tabla,tabla_update)

 #CASO 1


    elif ('AND' in inst or 'OR' in inst):
        if 'AND' in inst: ##SI ES SOLO ANDS
            w=re.split('[ ]*AND[ ]*',c1[0])

            for w1 in w:
                l=re.split('[ ]*=[ ]*',w1)
                for l1 in l:
                    where_c_v.append(l1.strip(' ').strip(';'))
            i=0
            while i<len(where_c_v): #comprabacion de que las columnas del where existen
                if i%2==0:
                    if (where_c_v[i] in primera_fila):
                        lista_indices_columnas_where.append(primera_fila.index(where_c_v[i]))
                        i+=1
                    else:
                        return print("La informacion solicitada no existe.")
                else:
                    where_valores.append(where_c_v[i])
                    i+=1

            i=1

            while i<len(tabla_update):
                bandera=len(lista_indices_columnas_where)
                x=tabla_update[i]
                for n in range(len(lista_indices_columnas_where)):
                    casilla=x[lista_indices_columnas_where[n]]
                    comparar=where_valores[n]
                    if casilla!=comparar.strip('\''):
                        break
                    else:
                        bandera=bandera-1

                if (bandera==0):
                    for k in range(len(lista_indice_set)): #por cada columna a guardar
                        numero = lista_indice_set[k] ##indice de columna a editar
                        x[numero] = lista_set_valores[k]
                    i+=1
                else:
                    i+=1

            actualizar_archivo(nombre_tabla,tabla_update)
            return print("Se ha insertado 1 fila .")

        else: #SOLO ORS
            w=re.split('[ ]*OR[ ]*',c1[0])

            for w1 in w:
                l=re.split('[ ]*=[ ]*',w1)
                for l1 in l:
                    where_c_v.append(l1.strip(' ').strip(';'))
            i=0
            while i<len(where_c_v): #comprabacion de que las columnas del where existen
                if i%2==0:
                    if (where_c_v[i] in primera_fila):
                        lista_indices_columnas_where.append(primera_fila.index(where_c_v[i]))
                        i+=1
                    else:
                        return print("La informacion solicitada no existe.")
                else:
                    where_valores.append(where_c_v[i])
                    i+=1
            i=1


            while i<len(tabla_update):

                x=tabla_update[i]
                for n in range(len(lista_indices_columnas_where)): #por cada columna where
                    casilla=x[lista_indices_columnas_where[n]]
                    comparar=where_valores[n]
                    if casilla==comparar.strip('\''):
                        for k in range(len(lista_indice_set)): #por cada columna a guardar
                            numero = lista_indice_set[k] ##indice de columna a editar
                            x[numero] = lista_set_valores[k]
                        i+=1
                i+=1

            actualizar_archivo(nombre_tabla,tabla_update)
            return print("Se ha actualizado 1 fila .") #CASO 2

    else:

        lista_indice_de_columnas=[]
        lista_indice_de_valores=[]

        i=0
        while i<len(columnas_where):  #verifica si existe la columna del where:
            if i%2==0:
                if (columnas_where[i] in primera_fila):
                    lista_indice_de_columnas.append(primera_fila.index(columnas_where[i]))
                    i+=1
                else:
                    return print("no existe la columna")
            i+=1

        i=0
        j=0

        while i<len(columnas_where):
            pos=lista_indice_de_columnas[0]

            if i%2==1:
                for j in tabla_update:
                    if columnas_where[i]==j[pos]:
                        lista_indice_de_valores.append(tabla_update.index(j))
                    else:
                        continue
                i+=1
            else:
                i+=1


        i=0
        while i<len(columnas_f1):
            if i%2==0:
                if (columnas_f1[i] in primera_fila):
                    lista_indice_set.append(primera_fila.index(columnas_f1[i]))
                    i+=1
                else:
                    return print("no existe la columna")
                    i+=1
            else:
                i+=1

        j=0
        i=0
        while j<len(tabla_update):
            if j in lista_indice_de_valores:
                tabla_update[j][lista_indice_set[0]]=columnas_f1[1]
                i+=1
                j+=1
            else:
                j+=1
        actualizar_archivo(nombre_tabla,tabla_update)

        return print('Se ha actualizado ',i,' filas')
####################################################################

#Nombre: Separar
#Entrada: instruccion de tipo string, dada por el usuario y la primera fila de la tabla
#Salida: no retorna nada

#Descripcion:separa columnas entre select y from retorna los indices de esas columnas en la primera fila de la tabla

def separar(comando,primera_fila):
    ind = comando.index('FROM')
    cf = []
    columnas = []
    i=1
    if (ind-1==1):
        while i < ind:
            comando1 = re.split(',',comando[i])
            i+=1
        x=comando1[0]
        if x in primera_fila:
            a = primera_fila.index(x)
            cf.append(a)
            return cf
        else:
            return -1
    else:
        i=1
        while i < ind:
            columnas.append(comando[i])
            i+=1
        i=0
        columnas_finales = []
        while i<len(columnas):
            if i==0:
                columnas_finales.append(columnas[i])
                i+=1
            elif i%2 ==0:
                columnas_finales.append(columnas[i])
                i+=1
            else:
                i+=1


        for x in columnas_finales:
            if x in primera_fila:
                a = primera_fila.index(x)
                cf.append(a)
            else:
                return -1

        cf.sort()
        return cf
####################################################################
#Nombre: imprimir
#Entrada: lista a imprimir
#Salida: no retorna nada

#Descripcion:imprime tablsa guardadas en listas de listas

def imprimir(lista):
    for k in lista:
         for x1 in k:
             print(x1,end=' ')
         print(" ")
####################################################################
#Nombre: indentificador
#Entrada: recibe el comando ingresado por consola
#Salida: retorna el numero de caso para la ejecucion del archivo

#Descripcion:identifica el caso de select ingresado por el usuario

def identificador (comando) : #La idea es que esta funcion reciba el comando y sea capaz de identficar los tokems y CASOS, ASUME QUE NO HAY ERROR DE SINTAXIS

    command = re.split(r'[ ]+',comando) ##comando guardado en una lista y separado por espacios

    if ('INNER' in command and 'JOIN' in command ): #CON INNER
        if ('WHERE' in command and ('AND' in command or 'OR' in command)):
            if ('ORDER BY' in command and 'BY' in command ):
                return 1
            else:
                return 2
        elif ('WHERE' in command and 'ORDER' in command and 'BY' in command):
            return 3
        else :
            return 4

    elif ('WHERE' in command): ## CON WHERE
        if ('WHERE' in command and ('AND' in command or 'OR' in command)):
            if ('ORDER BY' in command and 'BY' in command ):
                return 5
            else:
                return 6

        elif ('WHERE' in command and 'ORDER' in command and 'BY' in command):
            return 7
        else :
            return 8

    elif ('ORDER' in command and 'BY' in command): #solo con order
            return 9

    else : ##sin sentencias extras
        return 10

####################################################################
#Nombre: caso6
#Entrada: recibe el codigo que identifica * | columnas , la tabla de select, el comando separado por espacios, y el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado

#Descripcion:selecciona lo pedido segun el caso 6

def caso6(codigo,tabla_select,sentencia,comando):  # SELECT Rol, Ramo FROM Notas WHERE Nombre=\'Gabriel Carmona\' AND Nota=70;
    if (codigo==0):##SOLO CON AND y  ORS POR SEPARADO y *
        if('AND' in comando and 'OR' not in comando):
            columnas_f1=[]
            lista_printear=[]
            lista_indice_select=[]
            lista_where_valores=[]
            primera_fila=tabla_select[0]
            p1_p2=re.split('WHERE',comando)
            p2 = p1_p2[1]
            p2_sin_and=re.split("[ ]*AND[ ]*",p2)

            for x in p2_sin_and:
                j=re.split('[ ]*=[ ]*',x)
                for j1 in j:
                    columnas_f1.append(j1.strip(' ').strip('\'').strip(';'))



            i=0
            while i<len(columnas_f1): ##comprobacion de que las columnas donde se hara set existan
                if i%2==0:
                    if(columnas_f1[i] in primera_fila):
                        lista_indice_select.append(primera_fila.index(columnas_f1[i]))
                        i+=1
                    else:
                        return print("La informacion solicitada no existe.")
                else:
                    lista_where_valores.append(columnas_f1[i])
                    i+=1


            i=1


            while i<len(tabla_select):
                bandera=len(lista_indice_select)
                x=tabla_select[i]
                for n in range(len(lista_indice_select)):
                    casilla=x[lista_indice_select[n]]
                    comparar=lista_where_valores[n]

                    if casilla!=comparar.strip('\'').strip('[ ]'):
                        break
                    else:
                        bandera=bandera-1
                        print("bandera nueva:",bandera)

                if (bandera==0):
                    lista_printear.append(x)
                    i+=1
                else:
                    i+=1

        elif('OR' in comando and 'AND' not in comando):
            columnas_f1=[]
            lista_printear=[]
            lista_indice_select=[]
            lista_where_valores=[]
            print(sentencia)
            primera_fila=tabla_select[0]
            p1_p2=re.split('WHERE',comando)
            p2 = p1_p2[1]
            p2_sin_and=re.split("[ ]*OR[ ]*",p2)

            for x in p2_sin_and:
                j=re.split('[ ]*=[ ]*',x)
                for j1 in j:
                    columnas_f1.append(j1.strip(' ').strip('\'').strip(';'))
            print("columnas f1",columnas_f1)


            i=0
            while i<len(columnas_f1): ##comprobacion de que las columnas donde se hara set existan
                if i%2==0:
                    if(columnas_f1[i] in primera_fila):
                        lista_indice_select.append(primera_fila.index(columnas_f1[i]))
                        i+=1
                    else:
                        return print("La informacion solicitada no existe.")
                else:
                    lista_where_valores.append(columnas_f1[i])
                    i+=1
            print(lista_where_valores)
            print(lista_indice_select)

            i=1

            while i<len(tabla_select):

                x=tabla_select[i]
                for n in range(len(lista_indice_select)):
                    casilla=x[lista_indice_select[n]]
                    comparar=lista_where_valores[n]
                    if casilla==comparar.strip('\'').strip('[ ]'):
                        lista_printear.append(x)
                i+=1
            imprimir(lista_printear)
####################################################################
#Nombre: caso7
#Entrada: recibe el codigo que identifica * | columnas , la tabla de select, el comando separado por espacios, y el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado

#Descripcion:selecciona lo pedido segun el caso 7
def caso7(codigo,tabla_select,sentencia,comando): #SELECT FROM WHERE ORDER BY
####################################################################
#Nombre: caso8
#Entrada: recibe el codigo que identifica * | columnas , la tabla de select, el comando separado por espacios, y el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado

#Descripcion:selecciona lo pedido segun el caso 8
def caso8 (codigo,tabla_select,sentencia,comando):

    primera_fila = tabla_select[0]
    printear = []
    printear_aux = []
    a4=[]

    a = re.split('WHERE',comando) #lista separada por where (es decir, sin where)
    a2 = a[1] #parte derecha del where
    a3 = re.split("[ ]*=[ ]*",a2)#separado por el =

    for j in a3:
        c = j.strip('[ ]').strip('[ ]*;')
        a4.append(c)

    if (a4[0] in primera_fila):
        indice = primera_fila.index(a4[0])

        if codigo==0:

            if (er_valores.fullmatch(a4[1])):
                i=1
                while i<len(tabla_select):
                    x = tabla_select[i]
                    x1 = x[indice]
                    if (x1 in a4[1]):
                        printear.append(x)
                        i+=1
                    else:
                        i+=1

                if (len(printear)!=0):
                    imprimir(printear)
                else:
                    return print("La informacion solicitada no existe.")

            else :
                if (a4[1] in primera_fila):
                    indice1 = primera_fila.index(a4[1])
                    i=1
                    while i<len(tabla_select):
                        x = tabla_select[i]
                        x1 = x[indice]

                        if (x1==x1[indice1] ):
                            printear.append[x]
                            i+=1

                        else:
                            i+=1

                    if (len(printear)!=0):
                        imprimir(printear)
                    else:
                        return print("La informacion solicitada no existe.")
                else:
                    return print("La informacion solicitada no existe.")

        else :## muchas columnas entre select y from
            columnass = separar(sentencia,primera_fila) #lista de indices de columnas a seleccionar

            if columnass!= -1:
                if (er_valores.fullmatch(a4[1])): #valor
                    i=1

                    while i<len(tabla_select):
                        x = tabla_select[i]
                        x1 = x[indice]

                        if (x1 in a4[1]):
                            printear_aux.append(x)
                            i+=1
                        else:
                            i+=1


                    if (len(printear_aux)!=0):

                        i=0
                        while i < len(printear_aux):
                            sub_tabla = []
                            for x in columnass:
                                fila=printear_aux[i]
                                sub_tabla.append(fila[x])
                            printear.append(sub_tabla)
                            i+=1

                        imprimir(printear)

                    else:
                        return print("La informacion solicitada no existe.")

                else:
                    indice1 = primera_fila.index(a4[1])

                    i=1
                    while i<len(tabla_select):
                        x = tabla_select[i]
                        x1 = x[indice]
                        if (x1==x[indice1] ):
                            printear_aux.append(x)
                            i+=1
                        else:
                            i+=1

                    if (len(printear_aux)!=0):
                        i=0
                        while i<len(printear_aux):
                            sub_tabla=[]
                            for x in columnass:
                                fila=printear_aux[i]
                                sub_tabla.append(fila[x])
                            printear.append(sub_tabla)
                            i+=1

                        imprimir(printear)

                    else:
                        return print("La informacion solicitada no existe.")
            else:
                return print("La informacion solicitada no existe.")

    else :
        return print("La informacion solicitada no existe.")
####################################################################
#Nombre: caso9
#Entrada: recibe el codigo que identifica * | columnas , la tabla de select, el comando separado por espacios, y el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado

#Descripcion:selecciona lo pedido segun el caso 9
def caso9 (codigo,tabla_select,sentencia):

    orderBy = sentencia[sentencia.index('BY')+1]
    primera_fila = tabla_select[0]
    if (orderBy in primera_fila): #con esto verifico que lo que voy a ordenar sea una columna de la tabla
        i_orderBy = primera_fila.index(orderBy)

        if (codigo==0):

            if ('ASC' in sentencia):
                lista_asc = []
                i=1
                while i<len(tabla_select):
                    lista_asc.append(tabla_select[i])
                    i+=1
                lista_asc.sort(key=lambda lista_asc : lista_asc[i_orderBy])

            else:
                lista_DESC = []
                i=1
                while i<len(tabla_select):
                    lista_DESC.append(tabla_select[i])
                    i+=1
                lista_DESC.sort(key=lambda lista_DESC : lista_DESC[i_orderBy], reverse=True)



        else : ##MUCHAS columnas entre select from
            columnass = separar(sentencia,primera_fila) #lista de indices de columnas a seleccionar
            if columnass != -1 :
                columnass.append(i_orderBy)
                largo=len(columnass)-1
                lista_para_ordenar = []
                printear=[]

                i=1
                while i < len(tabla_select):
                    sub_tabla = []
                    for x in columnass:
                        fila=tabla_select[i]
                        sub_tabla.append(fila[x])
                    lista_para_ordenar.append(sub_tabla)
                    i+=1

                if ('ASC' in sentencia):

                    lista_para_ordenar.sort(key=lambda lista_para_ordenar : lista_para_ordenar[len(columnass)-1])

                    for fila in lista_para_ordenar:
                        printear.append(fila[0:largo])

                else:


                    lista_para_ordenar.sort(key=lambda lista_para_ordenar : lista_para_ordenar[len(columnass)-1], reverse=True)

                    for fila in lista_para_ordenar:
                        printear.append(fila[0:largo])

                imprimir(printear)

            else :
                return print("La informacion solicitada no existe.")
    else :
        return print("La informacion solicitada no existe.")
####################################################################
#Nombre: caso10
#Entrada: recibe el codigo que identifica * | columnas , la tabla de select, el comando separado por espacios, y el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado

#Descripcion:selecciona lo pedido segun el caso 10
def caso10 (codigo,tabla_select,sentencia):

    i=1
    primera_fila=tabla_select[0]
    printear=[]

    if (codigo==0):
        while i<len(tabla_select):
            for x in tabla_select[i]:
                print (x,end=' ')
            print (" ")
            i+=1
    else:
        columnass = separar(sentencia,primera_fila)

        if columnass != -1 :
            i=1
            while i<len(tabla_select):
                sub_tabla=[]
                fila=tabla_select[i]
                for x in columnass:
                    sub_tabla.append(fila[x])
                printear.append(sub_tabla)
                i+=1

            imprimir(printear)
        else :
            return print("La informacion solicitada no existe.")
####################################################################
#Nombre: select
#Entrada: recibe el comando ingresado por el usuario
#Salida: imprime por consola lo seleccionado por el usuario

#Descripcion:selecciona lo pedido por el usuario
def select(comando) :

    dic_de_tablas = { }

    id = identificador(comando)
    sentencia = re.split(r'[ ]+',comando)
    nombre_tabla1 = sentencia[sentencia.index('FROM')+1]
    nombre_tabla1 = nombre_tabla1.strip(' ').split(',')
    guardar_tabla(nombre_tabla1[0],dic_de_tablas)
    tabla_select = dic_de_tablas[nombre_tabla1[0]]

    if (sentencia[1]== '*'):
        codigo = 0
    else:
        codigo = 1
    if id==10:
        caso10(codigo,tabla_select,sentencia)
    elif id==9:
        caso9(codigo,tabla_select,sentencia)
    elif id==8:
        caso8(codigo,tabla_select,sentencia,comando)
    elif id==7:
        caso7(codigo,tabla_select,sentencia,comando)
    else:
        caso6(codigo,tabla_select,sentencia,comando)
####################################################################
key=0
while key<1:
    comando = input("Ingrese comando SQL, presione 1 para salir: ")

    if comando!="1":

        llave = re.split('[ ]',comando) ##comando guardado en una lista y separado por espacios

        if('SELECT' in llave):
            a=revisar_sintaxis(comando)
            if a==1:
                select(comando)
            else:
                print ('Error de Sintaxis')
        elif('INSERT' in llave):
            a=revisar_sintaxis(comando)
            if a==1:
                insert(comando)
            else:
                print ('Error de Sintaxis')
        elif('UPDATE' in llave):
            a=revisar_sintaxis(comando)
            if a==1:
                update(comando)
            else:
                print ('Error de Sintaxis')
        else:
            print("Error de Sintaxis")
    else:
        key=2

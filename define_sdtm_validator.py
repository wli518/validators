from selenium import webdriver
import os
import xport
import PyPDF2
import re
##########################################################
def get_all_names(driver):
    links = driver.find_elements_by_tag_name('a')
    for link in links:
        attr_name = link.get_attribute("name")
        if attr_name is not None:
            id_link_list.add(attr_name)
###########################################################
def get_all_ids(driver,tags):
    for tag in tags:
        links = driver.find_elements_by_tag_name(tag)
        for link in links:
            attr_id = link.get_attribute("id")
            if attr_id is not None:
                id_link_list.add(attr_id)
###########################################################
def get_all_hyper_links(driver):
    links = driver.find_elements_by_tag_name('a')
    for link in links:
        attr_href=link.get_attribute("href")
        if attr_href is not None:
           if attr_href.endswith(".xpt"):
               xpt_link_list.add(attr_href)
           elif attr_href.find(".pdf") != -1:
               pdf_link_list.add(attr_href)
           else:
               short_link = attr_href.split('#')[1]
               internal_hyper_link_list.add(short_link)
############################################################
def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search
############################################################
def crf_validate_page(word,page):
    pdfFileObj = open(crf_path, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    totalpage=pdfReader.numPages
    if page > totalpage:
        print("page number is invalid")
        fw.write("page number is invalid\n")
        found=0;
    pageObj = pdfReader.getPage(page-1)
    try:
        for annot in pageObj['/Annots']:
            mynote=annot.getObject()['/Contents']
            if findWholeWord(word)(mynote) is not None:
               print(word+" can be compared with string \""+mynote+"\"")
               fw.write(word + " can be compared with string \"" + mynote + "\"\n")
               found = 1
               #break
    except:
        found=0
    finally:
        pdfFileObj.close()
    return(found)
############################################################
def crf_validate(attr,pages):
    for page in pages:
        if crf_validate_page(attr,page):
            print(attr +" is found in page "+str(page))
            fw.write(attr +" is found in page "+str(page)+"\n")
        else:
            print(attr + "is NOT found in page " + str(page))
            fw.write(attr + "is NOT found in page " + str(page)+"\n")
############################################################
def variable_meta_validation(driver):
    links=driver.find_elements_by_tag_name('table')
    for link in links:
        summary = link.get_attribute("summary")
        if  summary.startswith("ItemGroup IG.IG."):
            caption = link.find_element_by_tag_name("caption").text
            domain=caption[caption.index('(')+1:caption.index(')')]
            location=caption[caption.index('[')+1:caption.index(']')]
            #xptfile=location[10:]
            rows=link.find_elements_by_tag_name("tr")
            print("====================beginning of validation of variable metadata in crf for domain " + domain + "===============")
            fw.write("====================beginning of validation of variable metadata in crf for domain " + domain + "===============\n")
            for row in rows:
                tds=row.find_elements_by_tag_name("td")
                if len(tds) >0:
                    att_name=tds[0].text
                for td in tds:
                    if td.text is not None and td.text.startswith("CRF Page"):
                        print("-----------------------beginning of validation of variable " + att_name + "---------------")
                        fw.write("-----------------------beginning of validation of variable " + att_name + "---------------\n")
                        print(att_name+" should be in "+td.text)
                        fw.write(att_name + " should be in " + td.text+"\n")
                        ps = re.findall(r'\d+', td.text)
                        if '-' in td.text:
                             nums = range(int(ps[0]), int(ps[-1]) + 1)
                        else:
                            nums = [int(i) for i in ps]
                        crf_validate(att_name,nums)
                        print("-----------------------end of validation of variable "+att_name+"---------------------")
                        fw.write("-----------------------end of validation of variable "+att_name+"---------------------\n")
            print("====================end of validation of variable metadata in crf for domain "+domain+"=====================")
            print("====================end of validation of variable metadata in crf for domain " + domain + "=====================\n")
##############################################################
def xpt_validation(file, domain):
    if os.path.exists(file):
        try:
             with open(file, 'rb') as f:
                 num = 0
                 for row in xport.Reader(f):
                      print(row)
                      fw.write(str(row))
                      fw.write("\n")
                      num = num + 1
        except:
            print("fail to open " + file + " to read")
            fw.write("fail to open " + file + " to read\n")
            return (-1)
    else:
        return (-1)
    if num == 0:
        return (-1)
    else:
        return (num)
################################################################
def dataset_meta_validation(driver):
    link=driver.find_element_by_tag_name('table')
    rows=link.find_elements_by_tag_name("tr")
    for row in rows:
        if 'Structure' not in row.text:
           tds=row.find_elements_by_tag_name("td")
           dsname=tds[0].text
           xptfile=xpt_file_location+tds[6].text
           if xpt_validation(xptfile, dsname) > 0:
               print(dsname+" is good")
               fw.write(dsname+" is good\n")
           else:
               print(dsname + " is NOT good or is empty")
               fw.write(dsname + " is NOT good or is empty\n")
##################################################################
if __name__ == "__main__":
    chromedriver = "C:\Users\polly\Desktop\selenium-java-3.3.1\chromedriver"
    mydriver = webdriver.Chrome(chromedriver)
    define_xml_file="file:///C:/Users/polly/Desktop/define_learning/define_xml_2_0_releasepackage20140424/sdtm/define2-0-0-example-sdtm.html"
    mydriver.get(define_xml_file)

    xpt_file_location = "C://Users//polly//Desktop//define_learning//define_xml_2_0_releasepackage20140424//sdtm/"
    crf_path="C://Users//polly//Desktop//define_learning//define_xml_2_0_releasepackage20140424//sdtm//blankcrf.pdf"

    fw = open("C://Users//polly//Desktop//define_sdtm_validator_log.txt", "w")

    id_link_list = set()
    internal_hyper_link_list = set()
    xpt_link_list = set()
    pdf_link_list = set()

    print("Please wait a few minutes...")

    print("collecting all IDs and NAMEs for internal hyperlink")
    fw.write("collecting all IDs and NAMEs for internal hyperlink\n")
    mytags=['a','tr','div']
    get_all_ids(mydriver,mytags)
    get_all_names(mydriver)

    print("collecting all internal hyperlinks")
    fw.write("collecting all internal hyperlinks\n")
    get_all_hyper_links(mydriver)
    for ih in internal_hyper_link_list:
        if ih not in id_link_list:
            print("hyper link "+define_xml_file+"#"+ih+" is NOT good, please check define.xml")
            fw.write("hyper link "+define_xml_file+"#"+ih+" is NOT good,please check define.xml\n")

    print("validating datasets")
    fw.write("validating datasets\n")
    dataset_meta_validation(mydriver)

    print("validating variables in the dataset")
    fw.write("validating variables in the dataset\n")
    variable_meta_validation(mydriver)

    fw.close()
    mydriver.quit()

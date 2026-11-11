#include<stdio.h>
#include<stdlib.h>
#include<conio.h>
struct node{
int data;
strct node*add;
}
struct node*start=NULL,*temp,*new1;
void main(){
while(1){int choice;
  printf("---linked list---\n");
  printf("1.insert at beginning\n");
  printf("2.insert at end\n");
  printf("3.insert at any position\n");
  printf("4.delete from beggining\n");
  printf("5.delete from end\n");
  printf("6.delete from any position\n");
  printf("7.display\n");
  printf("8.exit\n");
  printf("9.create\n");
  printf("Enter your choice:");
  scanf("%d\n",&choice);

  switch(choice){
  case 1:
  insertAtBeggining();
  break;
  case 2:
  insertAtEnd();
  break;
  case 3:
  insertAtAnyPosition();
  break;
  case 4:
  deleteFromBeggining();
  break;
  case 5:
  deleteFromEnd();
  break;
  case 6:
  deleteFromAnyPosition();
  break;
  case 7:
  display();
  break;
  case 8:
  exit(0);
  break;
  case 9:
  create();
  break;
  default:
  printf("Invalide choice\n");
  }
}
}

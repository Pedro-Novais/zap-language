from core.model.enum import CommandTypeGet, CommandTypeSet


class CommandResponseBuilder:
    
    @staticmethod
    def response_for_reset_command() -> str:
        return "Mémoria do tutor resetada com sucesso!\n\n Pronto para começar uma nova conversa"
    
    @staticmethod
    def response_for_error_command() -> str:
        return "Comando não reconhecido. Por favor, verifique e tente novamente \n Caso precise de ajuda, utilize o comando '/help'."
    
    @staticmethod
    def response_for_help_command() -> str:
        return (
                "*Lista de comandos disponíveis:*\n\n"
                "*!reset* - Reseta a memória do tutor, iniciando uma nova conversa do zero.\n\n"
                "*/help* - Exibe esta mensagem de ajuda.\n\n"
                "_Para usar um comando, basta enviar a mensagem exatamente como escrita acima._"
            )   

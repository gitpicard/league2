import league2
import os
import game

if __name__ == '__main__':
    league2.init()

    settings = league2.Settings()
    settings.set_buffer_size((426, 240))
    settings.set_asset_folder(os.path.join(league2.get_executing_path(__file__), 'assets'))

    league2.run(game.RPGGame, settings)
    league2.quit()
